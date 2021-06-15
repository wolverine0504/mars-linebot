
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

from password import Password
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials

class PasswordDAO:
    # 上線後要改
    # db = firestore.Client(project=os.environ.get('GCP_PROJECT'))
    # passwords_ref=db.collection(u'passwords')

    #db = firestore.Client(project='ccs', credentials=AnonymousCredentials())

    # cred = credentials.Certificate("./mars-linebot-serviceAccount.json")
    # firebase_admin.initialize_app(cred)
    # db = firestore.client(project=os.environ.get('FIRESTORE_PROJECT_ID'))

    db = firestore.Client(project='ccs',credentials=AnonymousCredentials())
    passwords_ref = db.collection(u'passwords')

    # 新增資料時，若有重複資料，則採更新  傳入一個password object
    @classmethod
    def save_password(cls,password:Password)->None:
        #print("db:",cls.db)
        password_ref=cls.passwords_ref.document(password.password)
        #print("password_ref:", password_ref)
        password_doc=password_ref.get()
        #print("get_password_doc:",password_doc)
        if password_doc.exists:
            print(f"update {password.password} info")
            password_ref.set(document_data=password.to_dict(),merge=True)
        else:
            print(f"create new doc for {password.password}")
            cls.passwords_ref.add(document_data=password.to_dict(),document_id=password.password)

        return password.to_dict()

    #取用資料，開放以password的方式尋找 回傳password object
    @classmethod
    def get_password(cls,password:str)->Password:
        password_ref=cls.passwords_ref.document(password)
        password_doc = password_ref.get()
        if password_doc.exists:
            password=Password.from_dict(password_doc.to_dict())
            return password
        else:
            return False

