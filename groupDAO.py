
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

from group import Group
from google.cloud import firestore
# from google.auth.credentials import AnonymousCredentials

class GroupDAO:
    # 上線後要改
    # db = firestore.Client(project=os.environ.get('GCP_PROJECT'))
    # groups_ref=db.collection(u'groups')

    #db = firestore.Client(project='ccs', credentials=AnonymousCredentials())



    #db = firestore.Client(project='ccs',credentials=AnonymousCredentials())
    db = firestore.Client()
    groups_ref = db.collection(u'groups')

    # 新增資料時，若有重複資料，則採更新  傳入一個Group object
    @classmethod
    def save_group(cls,group:Group)->None:
        print("db:",cls.db)
        group_ref=cls.groups_ref.document(group.group_id)
        #print("group_ref:", group_ref)
        group_doc=group_ref.get()
        #print("get_group_doc:",group_doc)
        if group_doc.exists:
            print(f"update {group.group_id} info")
            group_ref.set(document_data=group.to_dict(),merge=True)
        else:
            print(f"create new doc for{group.group_id}")
            cls.groups_ref.add(document_data=group.to_dict(),document_id=group.group_id)

        return group.to_dict()

    #取用資料，開放以group_id的方式尋找 回傳Group object
    @classmethod
    def get_group(cls,group_id:str)->Group:
        group_ref=cls.groups_ref.document(group_id)
        group_doc = group_ref.get()
        if group_doc.exists:
            group=Group.from_dict(group_doc.to_dict())
        else:
            pass
        return group
