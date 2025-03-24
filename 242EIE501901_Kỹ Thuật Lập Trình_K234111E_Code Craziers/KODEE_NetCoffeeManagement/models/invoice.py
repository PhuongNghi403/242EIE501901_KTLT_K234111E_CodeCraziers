import logging
from datetime import datetime
from models.order import Order

# Cấu hình logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Invoice:
    """
    Class đại diện cho một hóa đơn
    """

    def __init__(self, id="", employee_id="", employee_name="", date="", time_period="", total=0, order=None):
        """
        Khởi tạo Invoice

        Args:
            id (str): ID hóa đơn
            employee_id (str): ID nhân viên
            employee_name (str): Tên nhân viên
            date (str): Ngày tạo hóa đơn (định dạng YYYY-MM-DD)
            time_period (str): Thời điểm trong ngày (Sáng, Chiều, Tối)
            total (int): Tổng tiền
            order (Order): Đơn hàng
        """
        self.id = id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.date = date
        self.time_period = time_period
        self.total = total
        self.order = order if order else Order()

    def to_dict(self):
        """
        Chuyển đổi Invoice thành dictionary

        Returns:
            dict: Dictionary chứa thông tin Invoice
        """
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'date': self.date,
            'time_period': self.time_period,
            'total': self.total,
            'order': self.order.to_dict()
        }

    @classmethod
    def from_dict(cls, data):
        """
        Tạo Invoice từ dictionary

        Args:
            data (dict): Dictionary chứa thông tin Invoice

        Returns:
            Invoice: Đối tượng Invoice
        """
        order_data = data.get('order', {})
        order = Order.from_dict(order_data)

        return cls(
            id=data.get('id', ''),
            employee_id=data.get('employee_id', ''),
            employee_name=data.get('employee_name', ''),
            date=data.get('date', ''),
            time_period=data.get('time_period', ''),
            total=data.get('total', 0),
            order=order
        )

