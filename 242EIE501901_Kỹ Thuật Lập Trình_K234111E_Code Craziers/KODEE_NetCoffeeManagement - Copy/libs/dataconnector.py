import os
import json
import logging

# Cấu hình logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataConnector:
    """
    Class kết nối và xử lý dữ liệu từ các file JSON
    """

    def __init__(self):
        """Khởi tạo DataConnector"""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset')

    def _load_json_file(self, filename):
        """
        Load dữ liệu từ file JSON

        Args:
            filename (str): Tên file JSON

        Returns:
            list: Danh sách dữ liệu từ file JSON
        """
        try:
            file_path = os.path.join(self.data_dir, filename)

            # Nếu file không tồn tại, trả về list rỗng
            if not os.path.exists(file_path):
                logger.warning(f"File {filename} doesn't exist, return empty list.")
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded data from file {filename}")
                return data
        except Exception as e:
            logger.error(f"Error loading file {filename}: {str(e)}")
            return []

    def save_json_file(self, filename, data):
        """
        Lưu dữ liệu vào file JSON

        Args:
            filename (str): Tên file JSON
            data (list): Dữ liệu cần lưu

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            file_path = os.path.join(self.data_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                logger.info(f"Saved data to file {filename}")
                return True
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            return False

    def load_employees(self):
        """
        Load danh sách nhân viên

        Returns:
            list: Danh sách nhân viên
        """
        return self._load_json_file('employees.json')

    def load_managers(self):
        """
        Load danh sách quản lý

        Returns:
            list: Danh sách quản lý
        """
        return self._load_json_file('managers.json')

    def load_menu_items(self):
        """
        Load danh sách món ăn

        Returns:
            list: Danh sách món ăn
        """
        return self._load_json_file('menu_items.json')

    def load_shifts(self):
        """
        Load danh sách ca làm

        Returns:
            list: Danh sách ca làm
        """
        return self._load_json_file('shifts.json')

    def load_invoices(self):
        """
        Load danh sách hóa đơn

        Returns:
            list: Danh sách hóa đơn
        """
        return self._load_json_file('invoices.json')

    def save_employee(self, employee):
        """
        Lưu thông tin nhân viên

        Args:
            employee (dict): Thông tin nhân viên

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            employees = self.load_employees()

            # Kiểm tra xem nhân viên đã tồn tại chưa
            for i, emp in enumerate(employees):
                if emp.get('id') == employee.get('id'):
                    # Cập nhật thông tin nhân viên
                    employees[i] = employee
                    return self.save_json_file('employees.json', employees)

            # Thêm nhân viên mới
            employees.append(employee)
            return self.save_json_file('employees.json', employees)
        except Exception as e:
            logger.error(f"Error saving employee information: {str(e)}")
            return False

    def save_manager(self, manager):
        """
        Lưu thông tin quản lý

        Args:
            manager (dict): Thông tin quản lý

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            managers = self.load_managers()

            # Kiểm tra xem quản lý đã tồn tại chưa
            for i, mgr in enumerate(managers):
                if mgr.get('id') == manager.get('id'):
                    # Cập nhật thông tin quản lý
                    managers[i] = manager
                    return self.save_json_file('managers.json', managers)

            # Thêm quản lý mới
            managers.append(manager)
            return self.save_json_file('managers.json', managers)
        except Exception as e:
            logger.error(f"Error saving manager information: {str(e)}")
            return False

    def save_menu_item(self, menu_item):
        """
        Lưu thông tin món ăn

        Args:
            menu_item (dict): Thông tin món ăn

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            menu_items = self.load_menu_items()

            # Kiểm tra xem món ăn đã tồn tại chưa
            for i, item in enumerate(menu_items):
                if item.get('id') == menu_item.get('id'):
                    # Cập nhật thông tin món ăn
                    menu_items[i] = menu_item
                    return self.save_json_file('menu_items.json', menu_items)

            # Thêm món ăn mới
            menu_items.append(menu_item)
            return self.save_json_file('menu_items.json', menu_items)
        except Exception as e:
            logger.error(f"Error saving menu item information: {str(e)}")
            return False

    def delete_menu_item(self, menu_id):
        """
        Xóa món ăn

        Args:
            menu_id (str): ID món ăn cần xóa

        Returns:
            bool: True nếu xóa thành công, False nếu có lỗi
        """
        try:
            menu_items = self.load_menu_items()

            # Lọc ra các món ăn không có ID trùng với menu_id
            new_menu_items = [item for item in menu_items if item.get('id') != menu_id]

            # Nếu số lượng món ăn không thay đổi, tức là không tìm thấy món ăn cần xóa
            if len(new_menu_items) == len(menu_items):
                logger.warning(f"No menu item found with ID {menu_id}")
                return False

            return self.save_json_file('menu_items.json', new_menu_items)
        except Exception as e:
            logger.error(f"Error deleting menu item: {str(e)}")
            return False

    def save_shift(self, shift):
        """
        Lưu thông tin ca làm

        Args:
            shift (dict): Thông tin ca làm

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            shifts = self.load_shifts()

            # Kiểm tra xem ca làm đã tồn tại chưa
            for i, s in enumerate(shifts):
                if s.get('id') == shift.get('id'):
                    # Cập nhật thông tin ca làm
                    shifts[i] = shift
                    return self.save_json_file('shifts.json', shifts)

            # Thêm ca làm mới
            shifts.append(shift)
            return self.save_json_file('shifts.json', shifts)
        except Exception as e:
            logger.error(f"Error saving shift information: {str(e)}")
            return False

    def delete_shift(self, shift_id):
        """
        Xóa ca làm

        Args:
            shift_id (str): ID ca làm cần xóa

        Returns:
            bool: True nếu xóa thành công, False nếu có lỗi
        """
        try:
            shifts = self.load_shifts()

            # Lọc ra các ca làm không có ID trùng với shift_id
            new_shifts = [shift for shift in shifts if shift.get('id') != shift_id]

            # Nếu số lượng ca làm không thay đổi, tức là không tìm thấy ca làm cần xóa
            if len(new_shifts) == len(shifts):
                logger.warning(f"No shift found with ID {shift_id}")
                return False

            return self.save_json_file('shifts.json', new_shifts)
        except Exception as e:
            logger.error(f"Error deleting shift: {str(e)}")
            return False

    def save_invoice(self, invoice):
        """
        Lưu thông tin hóa đơn

        Args:
            invoice (dict): Thông tin hóa đơn

        Returns:
            bool: True nếu lưu thành công, False nếu có lỗi
        """
        try:
            invoices = self.load_invoices()

            # Kiểm tra xem hóa đơn đã tồn tại chưa
            for i, inv in enumerate(invoices):
                if inv.get('id') == invoice.get('id'):
                    # Cập nhật thông tin hóa đơn
                    invoices[i] = invoice
                    return self.save_json_file('invoices.json', invoices)

            # Thêm hóa đơn mới
            invoices.append(invoice)
            return self.save_json_file('invoices.json', invoices)
        except Exception as e:
            logger.error(f"Error saving invoice information: {str(e)}")
            return False

    def delete_invoice(self, invoice_id):
        """
        Xóa hóa đơn

        Args:
            invoice_id (str): ID hóa đơn cần xóa

        Returns:
            bool: True nếu xóa thành công, False nếu có lỗi
        """
        try:
            invoices = self.load_invoices()

            # Lọc ra các hóa đơn không có ID trùng với invoice_id
            new_invoices = [invoice for invoice in invoices if invoice.get('id') != invoice_id]

            # Nếu số lượng hóa đơn không thay đổi, tức là không tìm thấy hóa đơn cần xóa
            if len(new_invoices) == len(invoices):
                logger.warning(f"No invoice found with ID {invoice_id}")
                return False

            return self.save_json_file('invoices.json', new_invoices)
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}")
            return False
