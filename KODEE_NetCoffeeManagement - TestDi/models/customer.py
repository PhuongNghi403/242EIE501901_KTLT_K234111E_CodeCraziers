import json


class Customer:
    def __init__(self, id="", name="", phone=""):
        self.id = id
        self.name = name
        self.phone = phone

    def to_dict(self):
        """Chuyển đổi đối tượng thành dictionary để lưu vào JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data):
        """Tạo đối tượng từ dictionary được đọc từ JSON"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            phone=data.get("phone", "")
        )

    def to_json(self):
        """Chuyển đổi đối tượng thành chuỗi JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str):
        """Tạo đối tượng từ chuỗi JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __str__(self):
        return f"Customer(id={self.id}, name={self.name}, phone={self.phone})"

    def __repr__(self):
        return self.__str__()