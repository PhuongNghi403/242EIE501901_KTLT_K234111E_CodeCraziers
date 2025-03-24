class Shift:
    def __init__(self, id="", name="", employee_id="", employee_name="", date=""):
        self.id = id
        self.name = name
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.date = date

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            employee_id=data.get('employee_id', ''),
            employee_name=data.get('employee_name', ''),
            date=data.get('date', '')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'date': self.date
        }
