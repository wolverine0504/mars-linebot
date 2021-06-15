
class Password:

        def __init__(self, password,used,salt):
            self.password = password
            self.used = used
            self.salt=salt

        @staticmethod
        def from_dict(source: dict):
            password=Password(
                password=source.get("password"),
                used=source.get("used"),
                salt=source.get("salt")
            )
            return password


        def to_dict(self):
            password_dict={
                "password":self.password,
                "used":self.used,
                "salt":self.salt,
            }
            return password_dict

        def __repr__(self):
            return (f'''Password(
                    password={self.password},
                    used={self.used},
                    salt={self.salt}
                    )'''
                    )