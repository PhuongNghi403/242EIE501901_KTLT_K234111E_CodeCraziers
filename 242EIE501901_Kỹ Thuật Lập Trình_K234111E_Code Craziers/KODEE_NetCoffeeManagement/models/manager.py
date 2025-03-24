class Manager:
    def __init__(self, id="", name="", password=""):
        self.id = id
        self.name = name
        self.password = password

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            password=data.get('password', '')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password
        }
