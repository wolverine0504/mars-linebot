
class Group(object):

    #直接用建構宣告一個group
    def __init__(self, group_id,group_name,group_password,password_used,group_count,last_message,expected_text,status):
        self.group_id = group_id
        self.group_name=group_name
        self.group_password=group_password
        self.password_used=password_used
        self.group_count=group_count
        self.last_message=last_message
        self.expected_text=expected_text
        self.status=status
    #直接以class呼叫即可 將group dict 轉換成 group object

    #-> Group ????

    @staticmethod
    def from_dict(source:dict):
        group=Group(
            group_id=source.get("group_id"),
            group_name=source.get("group_name"),
            group_password=source.get("group_password"),
            password_used=source.get("password_used"),
            group_count=source.get("group_count"),
            last_message=source.get("last_message"),
            expected_text=source.get("expected_text"),
            status=source.get("status"),
            )
        return group

    #只能用group instance呼叫 將group object 轉成 dict
    def to_dict(self):
        group_dict = {
            "group_id": self.group_id,
            "group_name":self.group_name,
            "group_password": self.group_password,
            "password_used": self.password_used,
            "group_count":self.group_count,
            "last_message": self.last_message,
            "expected_text": self.expected_text,
            "status":self.status,
        }
        return group_dict

    def __repr__(self):
        return (f'''Group(
               group_id={self.group_id},
               group_name={self.group_name},
               group_password={self.group_password},
               password_used={self.password_used},
               group_count={self.group_count},
               last_message={self.last_message},
               expected_text={self.expected_text},
               status={self.status}
               )'''
                )