from flask import Flask, request, abort

import pandas as pd
import os
import json
import random
import hashlib
import string
import openpyxl
from urllib import parse

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction,
    PostbackAction, ImagemapSendMessage, ImageSendMessage, StickerSendMessage, AudioSendMessage, LocationSendMessage,
    FlexSendMessage, VideoSendMessage,
)
from linebot.models.events import JoinEvent, PostbackEvent,MemberJoinedEvent,MemberLeftEvent

from group import Group
from groupDAO import GroupDAO

from password import Password
from passwordDAO import PasswordDAO

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))


#根據passwords excel產生hash字串密碼
#在表中新增 hash過的遊戲包密碼
def generate_password():
    password_table=pd.read_excel('passwords.xlsx',engine='openpyxl')
    password_table.columns = ['index', 'password']
    for index, password in password_table['password'].items():
        hash_object = hashlib.sha256(str(password).encode('utf-8'))
        print('new Hashed password saved:', hash_object.hexdigest())
        password=Password(hash_object.hexdigest(),False,"famous_cookie")
        PasswordDAO.save_password(password)

generate_password()



def getMessageObject(jsonObject):
    message_type = jsonObject.get('type')
    if message_type == 'text':
        return TextSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'imagemap':
        return ImagemapSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'template':
        return TemplateSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'image':
        return ImageSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'sticker':
        return StickerSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'audio':
        return AudioSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'location':
        return LocationSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'flex':
        return FlexSendMessage.new_from_json_dict(jsonObject)
    elif message_type == 'video':
        return VideoSendMessage.new_from_json_dict(jsonObject)


def get_reply_messages(data):
    querystring_dict = dict(parse.parse_qsl(data))
    section=querystring_dict['section']
    action=querystring_dict['action']
    reply_table = pd.read_excel('reply_messages.xlsx', engine='openpyxl')
    section_row = reply_table[reply_table.section == section ]
    action_row = section_row[section_row.action == action]
    return_array = []
    for i in range(5):
        if not pd.isna(action_row['message' + str(i + 1)].values[0]):
            print("massage json string: ",action_row['message' + str(i + 1)].values[0])
            print(type(action_row['message' + str(i + 1)].values[0]))
            jsonObject = json.loads(action_row['message' + str(i + 1)].values[0]) #string to dict
            messageObject = getMessageObject(jsonObject)
            return_array.append(messageObject)

    print("generate reply messages:",return_array)
    return return_array

def get_reply_message_dict(data):
    querystring_dict = dict(parse.parse_qsl(data))
    section = querystring_dict['section']
    action = querystring_dict['action']
    reply_table = pd.read_excel('reply_messages.xlsx', engine='openpyxl')
    section_row = reply_table[reply_table.section == section]
    action_row = section_row[section_row.action == action]
    return action_row.to_dict('records')[0]


def get_response(expected_text,answer):
    response_table=pd.read_excel('expected_message.xlsx',engine='openpyxl')
    response_rows=response_table[response_table.expected_text==expected_text]
    response_rows['possible_answer'] = response_rows['possible_answer'].apply(str)
    possible_answer_row=response_rows[response_rows.possible_answer==answer]

    #if possible_answer_row.shape[0]==1
    #有可能忘記放else
    if possible_answer_row.empty:#沒找到用戶輸入答案的對應response 回傳else的response
        else_response=response_rows[response_rows.possible_answer=='else']
        else_response_dict=else_response.to_dict('records')[0]
        return else_response_dict['response']
    else:
        response_dict = possible_answer_row.to_dict('records')[0]
        return response_dict['response']

def check_group_status(event):
    group = GroupDAO.get_group(event.source.group_id)
    if group.status == "active":
        return "active"
    elif group.status=="suspended":
        line_bot_api.reply_message(event.reply_token, get_reply_messages("section=auth&action=no_more_than_five"))
        return "suspended"
    elif group.status=="initial":
        return "initial"


def check_group_count_middleware(event):
    group_id=event.source.group_id
    group_count = line_bot_api.get_group_members_count(group_id)
    print(f"check group count for {group_id}:",group_count)
    group = GroupDAO.get_group(group_id)
    group.group_count=group_count
    GroupDAO.save_group(group)
    if group_count > 5:
        print("group_count > 5")
        group.status = "suspended"
        GroupDAO.save_group(group)
        line_bot_api.reply_message(event.reply_token, get_reply_messages("section=auth&action=no_more_than_five"))

    else:
        print("group_count <= 5")
        if group.status=="active":
           pass
        elif group.status=="initial":#人數正常但為輸入密碼
           print("initial group count pass sending last message:",group.last_message)
           line_bot_api.reply_message(event.reply_token, get_reply_messages(group.last_message))
        elif group.status=="suspended":#本來人數不對現在可以繼續
           group.status = "active"
           GroupDAO.save_group(group)
           line_bot_api.reply_message(event.reply_token, get_reply_messages(group.last_message))

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # print("post")
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msgtxt=event.message.text

    if check_group_status(event)=="suspended":
        print("ignore message from suspended group")
        return

    if msgtxt[0]=='#':
        print("ignore message by postback")
        return

    group = GroupDAO.get_group(event.source.group_id)
    expected_text=group.expected_text

    if expected_text=="password":#還沒輸入密碼開通
        hash_object = hashlib.sha256(str(msgtxt).encode('utf-8'))
        hashed_password=hash_object.hexdigest()
        password=PasswordDAO.get_password(hashed_password)
        if not password:#密碼不存在
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="這組密碼不存在喔！"))
        else:#密碼存在
            if password.used == True:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="這組密碼已經使用過喔！"))
            else:
                password.used = True
                PasswordDAO.save_password(password)
                group.status = "active"
                group.group_password = hashed_password
                group.password_used = True
                group.last_message = "section=kendo&action=first_message"
                group.expected_text = "nothing"
                GroupDAO.save_group(group)
                line_bot_api.reply_message(event.reply_token, get_reply_messages("section=kendo&action=first_message"))
    else:

        if msgtxt == "test":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="testing"))
        elif msgtxt == 'groupData':
            print(group)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(group)))
        elif msgtxt == '再說一次':
            line_bot_api.reply_message(event.reply_token, get_reply_messages(group.last_message))
        else:
                response_message=get_response(expected_text,msgtxt)
                print(response_message)
                print("type of:",type(response_message))
                if expected_text != "nothing":
                    reply_message = get_reply_message_dict(response_message)
                    group = GroupDAO.get_group(event.source.group_id)
                    group.last_message = response_message
                    group.expected_text = reply_message["expected_text"]
                    GroupDAO.save_group(group)
                    print(f"update group:{group.group_id} 's last_message to:{response_message}")
                    print(f"update group:{group.group_id} 's expected_text to:{reply_message['expected_text']}")

                line_bot_api.reply_message(event.reply_token, get_reply_messages(response_message))




@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    check_group_count_middleware(event)


@handler.add(MemberLeftEvent)
def handle_member_left(event):
    check_group_count_middleware(event)


@handler.add(JoinEvent)
def handle_join(event):

    print("join event")
    group_id = event.source.group_id
    summary = line_bot_api.get_group_summary(group_id)
    print("group_id:",summary.group_id)
    print("group_name:",summary.group_name)
    group_count = line_bot_api.get_group_members_count(group_id)
    print("group_count:",group_count)

    group=Group(group_id,summary.group_name,"0000",False,group_count,"section=auth&action=please_enter_password","password","initial")
    print("new group:",group)
    GroupDAO.save_group(group)

    check_group_count_middleware(event)



@handler.add(PostbackEvent)
def handle_postback(event):

    if check_group_status(event)=="suspended":
        print("ignore postback from suspended group")
        return

    data=event.postback.data
    print("received data:",data)
    reply_message=get_reply_message_dict(data)
    group=GroupDAO.get_group(event.source.group_id)
    group.last_message=data
    group.expected_text=reply_message["expected_text"]
    GroupDAO.save_group(group)
    print(f"update group:{group.group_id} 's last_message to:{data}")
    print(f"update group:{group.group_id} 's expected_text to:{reply_message['expected_text']}")

    line_bot_api.reply_message(event.reply_token,get_reply_messages(data) )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

