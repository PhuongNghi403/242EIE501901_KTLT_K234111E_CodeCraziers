import logging

# Cấu hình logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OrderItem:
    """
    Class đại diện cho một món ăn trong đơn hàng
    """

    def __init__(self, item_id="", name="", price=0, quantity=0):
        """
        Khởi tạo OrderItem

        Args:
            item_id (str): ID của món ăn
            name (str): Tên món ăn
            price (int): Giá món ăn
            quantity (int): Số lượng
        """
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        """
        Chuyển đổi OrderItem thành dictionary

        Returns:
            dict: Dictionary chứa thông tin OrderItem
        """
        return {
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }

    @classmethod
    def from_dict(cls, data):
        """
        Tạo OrderItem từ dictionary

        Args:
            data (dict): Dictionary chứa thông tin OrderItem

        Returns:
            OrderItem: Đối tượng OrderItem
        """
        return cls(
            item_id=data.get('item_id', ''),
            name=data.get('name', ''),
            price=data.get('price', 0),
            quantity=data.get('quantity', 0)
        )


class Order:
    """
    Class đại diện cho một đơn hàng
    """

    def __init__(self, customer_name="", customer_phone="", computer_id="", usage_time=0, usage_price=0):
        """
        Khởi tạo Order

        Args:
            customer_name (str): Tên khách hàng
            customer_phone (str): Số điện thoại khách hàng
            computer_id (str): ID máy tính
            usage_time (int): Thời gian sử dụng (giờ)
            usage_price (int): Giá tiền sử dụng máy
        """
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.computer_id = computer_id
        self.usage_time = usage_time
        self.usage_price = usage_price
        self.items = []

    def add_item(self, item):
        """
        Thêm món ăn vào đơn hàng

        Args:
            item (OrderItem): Món ăn cần thêm
        """
        try:
            # Kiểm tra xem món ăn đã tồn tại trong đơn hàng chưa
            for i, existing_item in enumerate(self.items):
                if existing_item.item_id == item.item_id:
                    # Cập nhật số lượng nếu món ăn đã tồn tại
                    self.items[i].quantity += item.quantity
                    logger.info(f"Cập nhật số lượng món {item.name} thành {self.items[i].quantity}")
                    return

            # Thêm món ăn mới vào đơn hàng
            self.items.append(item)
            logger.info(f"Thêm món {item.name} vào đơn hàng")
        except Exception as e:
            logger.error(f"Lỗi khi thêm món ăn vào đơn hàng: {str(e)}")

    def remove_item(self, item_id):
        """
        Xóa món ăn khỏi đơn hàng

        Args:
            item_id (str): ID món ăn cần xóa
        """
        try:
            # Lọc ra các món ăn không có ID trùng với item_id
            self.items = [item for item in self.items if item.item_id != item_id]
            logger.info(f"Xóa món có ID {item_id} khỏi đơn hàng")
        except Exception as e:
            logger.error(f"Lỗi khi xóa món ăn khỏi đơn hàng: {str(e)}")

    def get_total(self):
        """
        Tính tổng tiền đơn hàng

        Returns:
            int: Tổng tiền đơn hàng
        """
        try:
            # Tính tổng tiền món ăn
            food_total = sum(item.price * item.quantity for item in self.items)

            # Tổng tiền = tiền sử dụng máy + tiền món ăn
            total = self.usage_price + food_total

            logger.info(f"Tính tổng tiền đơn hàng: {total} VNĐ")
            return total
        except Exception as e:
            logger.error(f"Lỗi khi tính tổng tiền đơn hàng: {str(e)}")
            return 0

    def to_dict(self):
        """
        Chuyển đổi Order thành dictionary

        Returns:
            dict: Dictionary chứa thông tin Order
        """
        return {
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'computer_id': self.computer_id,
            'usage_time': self.usage_time,
            'usage_price': self.usage_price,
            'items': [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, data):
        """
        Tạo Order từ dictionary

        Args:
            data (dict): Dictionary chứa thông tin Order

        Returns:
            Order: Đối tượng Order
        """
        order = cls(
            customer_name=data.get('customer_name', ''),
            customer_phone=data.get('customer_phone', ''),
            computer_id=data.get('computer_id', ''),
            usage_time=data.get('usage_time', 0),
            usage_price=data.get('usage_price', 0)
        )

        # Thêm các món ăn vào đơn hàng
        for item_data in data.get('items', []):
            order.items.append(OrderItem.from_dict(item_data))

        return order

