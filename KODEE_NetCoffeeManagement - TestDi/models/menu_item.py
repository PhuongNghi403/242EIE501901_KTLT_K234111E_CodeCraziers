class MenuItem:
    def __init__(self, id="", name="", price=0, category="", order_count=0):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.order_count = order_count

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            price=data.get('price', 0),
            category=data.get('category', ''),
            order_count=data.get('order_count', 0)
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'order_count': self.order_count
        }
