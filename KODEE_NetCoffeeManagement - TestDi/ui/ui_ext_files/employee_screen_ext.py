from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMainWindow
import random
import datetime
import re
import os
import json
from models.server import ServerManager

from ui.ui_files.employee_screen import Ui_MainWindow


class employee_screen_ext(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.menu_items = {}  # Dictionary to store menu items and their quantities
        self.mainWindow = None
        self.current_employee = None
        self.server_manager = None
        self.current_server = None

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.mainWindow = MainWindow
        self.mainWindow.setWindowTitle("KODEE Management System")

        # Thêm khởi tạo server manager
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        dataset_path = os.path.join(project_root, 'dataset')
        server_json_path = os.path.join(dataset_path, 'servers.json')
        
        # Khởi tạo ServerManager với đường dẫn tới servers.json
        self.server_manager = ServerManager(server_json_path)

        # Setup Order Menu table
        self.setup_order_table()

        # Connect Menu buttons
        self.connect_menu_buttons()

        # Connect Server buttons
        self.connect_server_buttons()

        # Connect other buttons
        self.pushButtonLogOut.clicked.connect(self.exit_application)
        self.pushButtonXacNhanThanhToan.clicked.connect(self.confirm_payment)
        self.pushButtonXuatHoaDon.clicked.connect(self.generate_invoice)
        
        # Connect filter Radio Buttons
        self.radioButtonAvailable.toggled.connect(self.filter_servers)
        self.radioButton_Unavailable.toggled.connect(self.filter_servers)
        self.radioButtonAll.toggled.connect(self.filter_servers)

        # Setup invoice ID
        self.generate_invoice_id()

        # Setup date and time
        self.setup_datetime()

        # Connect time used spinbox
        self.spinBoxThoiGianSuDung.valueChanged.connect(self.update_time_calculations)

        # Initial update
        self.update_time_calculations()

        # Make sure all groupboxes are visible
        self.groupBoxCustomerInformation.show()
        self.groupBoxServiceInformation.show()
        self.groupBoxOrderMenu.show()

        # Set fixed heights for the groupboxes to ensure proper layout
        self.groupBoxCustomerInformation.setMinimumHeight(200)
        self.groupBoxServiceInformation.setMinimumHeight(250)
        self.groupBoxOrderMenu.setMinimumHeight(250)

    def set_current_employee(self, employee):
        """Đặt thông tin nhân viên hiện tại và hiển thị trên giao diện"""
        self.current_employee = employee
        if employee:
            # Hiển thị thông tin nhân viên đăng nhập ở label_EmployeeInfo
            employee_info = f"Signed in as: Employee - {employee['name']} ({employee['id']})"
            self.label_EmployeeInfo.setText(employee_info)

    def showWindow(self):
        self.mainWindow.show()

    def setup_order_table(self):
        """Setup the order table in the Order Menu group box"""
        # Create table widget
        self.tableOrderMenu = QTableWidget(self.groupBoxOrderMenu)
        self.tableOrderMenu.setColumnCount(5)
        self.tableOrderMenu.setHorizontalHeaderLabels(["Item ID", "Menu Item", "Quantity", "Price (VND)", "Total Amount"])

        # Set table properties
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Create a layout for the Order Menu groupbox if it doesn't exist
        if self.groupBoxOrderMenu.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.groupBoxOrderMenu)
            self.groupBoxOrderMenu.setLayout(layout)

        # Add table to the Order Menu groupbox
        self.groupBoxOrderMenu.layout().addWidget(self.tableOrderMenu)
        
        # Kết nối sự kiện double click để xóa món ăn
        self.tableOrderMenu.doubleClicked.connect(self.remove_menu_item)
        
        # Thêm button để xóa món ăn đã chọn
        self.pushButtonRemoveItem = QtWidgets.QPushButton(self.groupBoxOrderMenu)
        self.pushButtonRemoveItem.setText("Xóa món")
        self.pushButtonRemoveItem.clicked.connect(self.remove_selected_item)
        self.groupBoxOrderMenu.layout().addWidget(self.pushButtonRemoveItem)

    def connect_menu_buttons(self):
        """Connect all menu buttons to the add_menu_item function"""
        # Get all buttons in the Menu tab
        for i in range(1, 31):  # Assuming there are 30 menu buttons
            button_name = f"ButtonMenu{i}"
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.clicked.connect(self.add_menu_item)

    def filter_servers(self, checked=None):
        """Lọc danh sách server theo trạng thái được chọn bởi radio button"""
        # Bỏ qua lần gọi khi chỉ mới checked=False
        if checked is False and not hasattr(self, 'server_manager'):
            return
            
        if not self.server_manager:
            return
            
        # Xác định radio button nào được chọn
        if self.radioButtonAvailable.isChecked():
            # Lọc server có trạng thái available
            servers = self.server_manager.get_available_servers()
        elif self.radioButton_Unavailable.isChecked():
            # Lọc server có trạng thái occupied
            servers = self.server_manager.get_occupied_servers()
        else:  # RadioButtonAll hoặc trường hợp khác
            # Hiển thị tất cả server
            servers = self.server_manager.get_all_servers()
        
        # Cập nhật trạng thái các nút server
        self.update_server_buttons(servers)

    def update_server_buttons(self, filtered_servers=None):
        """Cập nhật trạng thái các nút server dựa trên danh sách server"""
        if not self.server_manager:
            return

        # Nếu không có danh sách lọc, lấy tất cả server
        if filtered_servers is None:
            filtered_servers = self.server_manager.get_all_servers()
        
        # Tạo dictionary để dễ dàng truy cập server theo ID
        server_dict = {server.id: server for server in filtered_servers}
        
        # Cập nhật trạng thái các nút server
        for i in range(1, 31):  # Giả sử có 30 server nút
            button_name = f"ButtonMay{i}"
            server_id = f"SE{i:02d}"
            
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                
                # Kiểm tra xem server có trong danh sách lọc không
                if server_id in server_dict:
                    button.show()  # Hiển thị nút nếu server trong danh sách lọc
                    server = server_dict[server_id]
                    
                    # Cập nhật màu sắc nút dựa trên trạng thái server
                    if server.status == "available":
                        # Màu tím cho server trống
                        button.setStyleSheet("background-color: rgb(229, 190, 236);")
                    else:
                        # Màu đỏ cho server đang sử dụng
                        button.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    # Ẩn nút nếu server không trong danh sách lọc
                    button.hide()

    def connect_server_buttons(self):
        """Connect all server buttons to the select_server function"""
        # Get all buttons in the Server tab
        for i in range(1, 31):  # Assuming there are 30 server buttons
            button_name = f"ButtonMay{i}"
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.clicked.connect(self.select_server)
        
        # Cập nhật trạng thái các nút server ban đầu
        self.update_server_buttons()

    def add_menu_item(self):
        """Add a menu item to the order table when a menu button is clicked"""
        # Get the sender button
        button = self.mainWindow.sender()
        if not button:
            return

        try:
            # Lấy thông tin nút
            button_name = button.objectName()
            button_text = button.text().strip()
            button_tooltip = button.toolTip().strip() if button.toolTip() else ""
            
            # Tìm thông tin món ăn từ nhiều nguồn
            item_info = None
            price_k = None
            item_id = None
            
            # Hiển thị thông tin debug để tìm ra vấn đề
            debug_info = f"Button name: {button_name}\nButton text: {button_text}\nTooltip: {button_tooltip}\n"
            
            # Phương pháp 1: Tìm trong tooltip (nếu có)
            if button_tooltip:
                # Giả định tooltip có thể chứa thông tin "Tên món: X, Giá: Y"
                item_match = re.search(r"Item:\s*(.*?),", button_tooltip)
                price_match = re.search(r"Price:\s*(\d+)", button_tooltip)
                
                if item_match and price_match:
                    item_info = item_match.group(1).strip()
                    price_k = int(price_match.group(1))
                    debug_info += f"Found from tooltip: {item_info}, {price_k}k\n"
            
            # Phương pháp 2: Tìm từ số ID của nút
            if not item_info and re.match(r"ButtonMenu(\d+)", button_name):
                button_id = re.match(r"ButtonMenu(\d+)", button_name).group(1)
                
                # Lấy dữ liệu từ dataset menu_items.json
                current_file = os.path.abspath(__file__)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                dataset_path = os.path.join(project_root, 'dataset')
                menu_items_path = os.path.join(dataset_path, 'menu_items.json')
                
                if os.path.exists(menu_items_path):
                    with open(menu_items_path, 'r', encoding='utf-8') as f:
                        menu_data = json.load(f)
                    
                    # Lấy món ăn tương ứng với button_id (giả sử thứ tự trong file khớp với thứ tự button)
                    button_index = int(button_id) - 1
                    if 0 <= button_index < len(menu_data):
                        menu_item = menu_data[button_index]
                        item_info = menu_item.get('name', '')
                        price_k = menu_item.get('price', 0) // 1000  # Chuyển từ VND sang k
                        item_id = menu_item.get('id', f'MI{button_index+1:02d}')  # Get menu item ID or generate one
                        debug_info += f"Found from dataset: {item_info}, {price_k}k, ID: {item_id}\n"
            
            # Phương pháp 3: Cố định một số giá trị mẫu cho mục đích kiểm tra
            if not item_info:
                # Tạo danh sách thực đơn mẫu 
                sample_menu = [
                    {"name": "Mì xào bò", "price": 40000},
                    {"name": "Mì xào trứng", "price": 30000},
                    {"name": "Mì xào bò trứng", "price": 45000},
                    {"name": "Nui xào trứng", "price": 30000},
                    {"name": "Nui xào bò", "price": 40000},
                    {"name": "Cơm chiên trứng", "price": 30000},
                    {"name": "Nước suối", "price": 10000},
                    {"name": "Sting", "price": 15000},
                    {"name": "Pepsi", "price": 15000},
                    {"name": "Trà sữa", "price": 25000}
                ]
                
                # Lấy một món ăn ngẫu nhiên từ danh sách mẫu
                import random
                sample_item = random.choice(sample_menu)
                item_info = sample_item["name"]
                price_k = sample_item["price"] // 1000
                debug_info += f"Using sample item: {item_info}, {price_k}k\n"
            
            # Nếu vẫn không tìm thấy thông tin món ăn, hiển thị thông báo và thoát
            if not item_info or not price_k:
                # Hiển thị thông tin debug để giúp tìm lỗi
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Debug Information")
                msg_box.setText(debug_info)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Error")
                msg_box.setText("Unable to read the food information. Please check the debug information.")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                return
            
            # Tính giá từ k sang VND
            price = price_k * 1000
                
            # Cập nhật từ điển menu_items
            if item_info in self.menu_items:
                self.menu_items[item_info]["quantity"] += 1
            else:
                self.menu_items[item_info] = {
                    "price": price,
                    "quantity": 1,
                    "id": item_id
                }
            
            # Cập nhật bảng
            self.update_order_table()
            
        except Exception as e:
            # Hiển thị lỗi chi tiết để dễ gỡ lỗi
            error_message = f"Error when processing food information: {str(e)}\n"
            error_message += f"Button name: {button.objectName() if button else 'Unknown'}\n"
            error_message += f"Button text: {button.text() if button else 'Unknown'}"
            
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Error")
            msg_box.setText(error_message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return

    def update_order_table(self):
        """Update the order table with the current menu items"""
        # Clear the table
        self.tableOrderMenu.setRowCount(0)

        # Add items to the table
        row = 0
        for item_name, details in self.menu_items.items():
            self.tableOrderMenu.insertRow(row)

            # Item ID
            item_id = details.get("id", "")
            self.tableOrderMenu.setItem(row, 0, QTableWidgetItem(item_id))

            # Item name
            self.tableOrderMenu.setItem(row, 1, QTableWidgetItem(item_name))

            # Quantity
            quantity = details["quantity"]
            self.tableOrderMenu.setItem(row, 2, QTableWidgetItem(str(quantity)))

            # Price
            price = details["price"]
            self.tableOrderMenu.setItem(row, 3, QTableWidgetItem(f"{price:,} VND"))

            # Total
            total = price * quantity
            self.tableOrderMenu.setItem(row, 4, QTableWidgetItem(f"{total:,} VND"))

            row += 1
        
        # Adjust column widths
        self.tableOrderMenu.setColumnWidth(0, 80)  # Item ID
        self.tableOrderMenu.setColumnWidth(1, 150)  # Item Name
        self.tableOrderMenu.setColumnWidth(2, 70)   # Quantity
        self.tableOrderMenu.setColumnWidth(3, 100)  # Price
        self.tableOrderMenu.setColumnWidth(4, 100)  # Total
        
        # Cập nhật tổng tiền
        self.update_time_calculations()

    def select_server(self):
        """Set the server number when a server button is clicked"""
        # Get the sender button
        button = self.mainWindow.sender()
        if not button:
            return

        # Get the button text (format: "Server X")
        button_text = button.text()

        # Extract the server number
        match = re.match(r"Server (\d+)", button_text)
        if not match:
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Invalid server format")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return

        server_number = match.group(1)
        server_id = f"SE{int(server_number):02d}"
        
        # Kiểm tra nếu đang chọn cùng một server (bấm 2 lần vào server)
        if self.lineEditServerMay.text() == server_id:
            # Reset server hiện tại
            self.current_server = None
            self.lineEditServerMay.clear()
            self.lineEditServerID.clear()  # Clear Server ID field
            
            # Đổi màu nút server về trạng thái available (màu tím)
            button.setStyleSheet("background-color: #E5BEEC;")
            return
        
        # Kiểm tra trạng thái server
        server = self.server_manager.get_server_by_id(server_id)
        if not server:
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Server not found {server_id}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return
        
        if not server.is_available():
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Server {server_id} is in use")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return
        
        # Nếu trước đó đã có server được chọn, reset style của server cũ về available
        if self.current_server:
            # Tìm button của server cũ
            old_server_number = int(self.current_server.id[2:])
            old_button_name = f"ButtonMay{old_server_number}"
            if hasattr(self, old_button_name):
                old_button = getattr(self, old_button_name)
                old_button.setStyleSheet("background-color: #E5BEEC;")
        
        # Lưu server hiện tại
        self.current_server = server
        
        # Set the server number in the line edit
        self.lineEditServerMay.setText(server_number)
        
        # Set the server ID in the Server ID field
        self.lineEditServerID.setText(server_id)
        
        # Đổi màu nút server đang chọn sang màu trắng
        button.setStyleSheet("background-color: rgb(255, 255, 255);")

    def generate_invoice_id(self):
        """Generate a sequential invoice ID in the format INxxx based on existing invoices"""
        # Get the path to invoices.json
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        dataset_path = os.path.join(project_root, 'dataset')
        invoices_json_path = os.path.join(dataset_path, 'invoices.json')

        # Find the highest invoice number
        highest_number = 0
        try:
            if os.path.exists(invoices_json_path):
                with open(invoices_json_path, 'r', encoding='utf-8') as f:
                    invoices = json.load(f)

                # Extract numbers from invoice IDs and find the highest
                for invoice in invoices:
                    invoice_id = invoice.get("id", "")
                    if invoice_id.startswith("IN"):
                        try:
                            number = int(invoice_id[2:])
                            highest_number = max(highest_number, number)
                        except ValueError:
                            # Skip if the number part is not a valid integer
                            pass
        except Exception as e:
            print(f"Error reading invoices for ID generation: {e}")
            # Fall back to random ID if there's an error
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(3)])
            invoice_id = f"IN{random_digits}"
            self.lineEditMaHoaDon.setText(invoice_id)
            self.lineEditMaHoaDon.setReadOnly(True)
            return

        # Generate the next invoice ID
        next_number = highest_number + 1
        invoice_id = f"IN{next_number:03d}"  # Format as IN001, IN002, etc.

        # Set the invoice ID in the line edit
        self.lineEditMaHoaDon.setText(invoice_id)
        self.lineEditMaHoaDon.setReadOnly(True)  # Make it read-only

    def setup_datetime(self):
        """Setup the date and time fields with current values"""
        # Get current date and time
        now = datetime.datetime.now()

        # Set the date
        self.dateEditThoiGianBill.setDate(QtCore.QDate(now.year, now.month, now.day))

        # Set the time in
        self.timeEditThoiGianVao.setTime(QtCore.QTime(now.hour, now.minute))

        # Make date and time in read-only
        self.dateEditThoiGianBill.setReadOnly(True)
        self.timeEditThoiGianVao.setReadOnly(True)
        self.timeEditThoiGianRa.setReadOnly(True)

    def setup_datetime(self):
        """Setup the date and time fields with current values"""
        # Get current date and time
        now = datetime.datetime.now()

        # Set the date
        self.dateEditThoiGianBill.setDate(QtCore.QDate(now.year, now.month, now.day))

        # Set the time in
        self.timeEditThoiGianVao.setTime(QtCore.QTime(now.hour, now.minute))

        # Make date and time in read-only
        self.dateEditThoiGianBill.setReadOnly(True)
        self.timeEditThoiGianVao.setReadOnly(True)
        self.timeEditThoiGianRa.setReadOnly(True)

    def update_time_calculations(self):
        """Update time-related calculations when time used changes"""
        # Get the time used value
        time_used = self.spinBoxThoiGianSuDung.value()

        # Calculate the amount for time used (10,000 VND per hour)
        amount = time_used * 10000
        self.lineEditServerMay_2.setText(f"{amount:,}")
        self.lineEditServerMay_2.setReadOnly(True)  # Make it read-only

        # Calculate time out based on time in and time used
        time_in = self.timeEditThoiGianVao.time()
        hours_in = time_in.hour()
        minutes_in = time_in.minute()

        # Add time_used hours to time_in
        total_minutes = hours_in * 60 + minutes_in + time_used * 60
        hours_out = total_minutes // 60
        minutes_out = total_minutes % 60

        # Handle overflow (more than 24 hours)
        hours_out = hours_out % 24

        # Set the time out
        self.timeEditThoiGianRa.setTime(QtCore.QTime(hours_out, minutes_out))

    def confirm_payment(self):
        """Handle payment confirmation"""
        try:
            # Check if required fields are filled
            if not self.lineEditTenKH.text():
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please enter the customer's name")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                return

            if not self.lineEditSoKH.text():
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please enter the customer's phone number")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                return

            if not self.lineEditServerMay.text():
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Please select the server machine")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                return

            # Calculate total amount
            total_amount = 0

            # Add menu items
            ordered_items = []
            for item_name, details in self.menu_items.items():
                price = details["price"]
                quantity = details["quantity"]
                item_id = details.get("id", "")
                total_amount += price * quantity
                
                # Add to ordered items list
                ordered_items.append({
                    "item_id": item_id,
                    "name": item_name,
                    "price": price,
                    "quantity": quantity
                })

            # Add time used amount
            time_used = self.spinBoxThoiGianSuDung.value()
            time_amount = time_used * 10000
            total_amount += time_amount
            
            # Get current date and time
            now = datetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            time_in = self.timeEditThoiGianVao.time().toString("HH:mm")
            time_out = self.timeEditThoiGianRa.time().toString("HH:mm")
            
            # Create invoice data
            # First, ensure current_employee is not None
            if not hasattr(self, 'current_employee') or self.current_employee is None:
                # Use default values if current_employee is None
                employee_id = "EMP001"
                employee_name = "Unknown Employee"
            else:
                employee_id = self.current_employee.get("id", "EMP001")
                employee_name = self.current_employee.get("name", "Unknown Employee")
                
            invoice_data = {
                "id": self.lineEditMaHoaDon.text(),
                "employee_id": employee_id,
                "employee_name": employee_name,
                "date": current_date,
                "time_in": time_in,
                "time_out": time_out,
                "total": total_amount,
                "order": {
                    "customer_name": self.lineEditTenKH.text(),
                    "customer_phone": self.lineEditSoKH.text(),
                    "computer_id": self.lineEditServerMay.text(),
                    "usage_time": time_used,
                    "usage_price": time_amount,
                    "items": ordered_items
                }
            }
            
            # Save to invoices.json
            try:
                # Get the path to invoices.json
                current_file = os.path.abspath(__file__)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                dataset_path = os.path.join(project_root, 'dataset')
                invoices_json_path = os.path.join(dataset_path, 'invoices.json')
                
                # Read existing invoices
                try:
                    with open(invoices_json_path, 'r', encoding='utf-8') as f:
                        invoices = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    invoices = []
                
                # Add new invoice
                invoices.append(invoice_data)
                
                # Write back to file
                with open(invoices_json_path, 'w', encoding='utf-8') as f:
                    json.dump(invoices, f, ensure_ascii=False, indent=4)
                    
                # Create a signal file to notify manager screen
                signal_file_path = os.path.join(dataset_path, 'new_invoice_signal.json')
                with open(signal_file_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "timestamp": now.timestamp(),
                        "invoice_id": invoice_data["id"]
                    }, f, ensure_ascii=False, indent=4)
                    
            except Exception as e:
                # Show error message instead of just printing to console
                error_msg = f"Error saving invoice: {e}"
                print(error_msg)
                
                msg_box = QMessageBox(self.mainWindow)
                msg_box.setWindowTitle("Error")
                msg_box.setText(f"An error occurred while saving the invoice:\n{error_msg}\nPlease try again.")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2A2F4F;
                        color: #FDE2F3;
                    }
                    QLabel {
                        color: #FDE2F3;
                    }
                    QPushButton {
                        background-color: #917FB3;
                        color: #FDE2F3;
                        padding: 5px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #E5BEEC;
                        color: #2A2F4F;
                    }
                """)
                
                msg_box.exec()
                return  # Exit the function if there's an error saving the invoice

            # Show confirmation message
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Payment Confirmation")
            msg_box.setText(f"Total Amount: {total_amount:,} VND\nPayment confirmation successful!\nInvoice has been saved.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            
            # If there's a current server selected, reset its button style
            if hasattr(self, 'current_server') and self.current_server:
                try:
                    server_number = int(self.current_server.id[2:])
                    button_name = f"ButtonMay{server_number}"
                    if hasattr(self, button_name):
                        button = getattr(self, button_name)
                        button.setStyleSheet("background-color: #E5BEEC;")
                except (AttributeError, ValueError, IndexError) as e:
                    print(f"Error resetting server button: {e}")
                
                # Reset current server
                self.current_server = None
            
            # Reset the form for new order
            self.reset_form()
            
        except Exception as e:
            # Catch any unexpected errors
            error_msg = f"Unexpected error in confirm_payment: {str(e)}"
            print(error_msg)
            
            # Display error message
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Critical Error")
            msg_box.setText(f"An unexpected error occurred:\n{error_msg}\n\nPlease try again.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()

    def generate_invoice(self):
        """Generate and display an invoice"""
        # Check if required fields are filled
        if not self.lineEditTenKH.text():
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please enter the customer's name")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return

        if not self.lineEditSoKH.text():
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Cảnh báo")
            msg_box.setText("Please enter the customer's phone number")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return

        if not self.lineEditServerMay.text():
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Cảnh báo") 
            msg_box.setText("Please select the server machine")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return

        # Calculate total amount
        total_amount = 0

        # Add menu items
        for item_name, details in self.menu_items.items():
            total_amount += details["price"] * details["quantity"]

        # Add time used amount
        time_used = self.spinBoxThoiGianSuDung.value()
        time_amount = time_used * 10000
        total_amount += time_amount

        # Prepare invoice text
        invoice_text = f"""
        KODEE MANAGEMENT SYSTEM
        ----------------------
        Invoice ID: {self.lineEditMaHoaDon.text()}
        Date: {self.dateEditThoiGianBill.date().toString("dd/MM/yyyy")}
        Time: {self.timeEditThoiGianVao.time().toString("hh:mm")} - {self.timeEditThoiGianRa.time().toString("hh:mm")}

        Customer: {self.lineEditTenKH.text()}
        Phone: {self.lineEditSoKH.text()}
        Server: {self.lineEditServerMay.text()}

        ORDERED ITEMS:
        """

        # Add menu items to invoice
        for item_name, details in self.menu_items.items():
            price = details["price"]
            quantity = details["quantity"]
            total = price * quantity
            invoice_text += f"\n{item_name} x{quantity}: {total:,} VND"

        # Add time used to invoice
        invoice_text += f"\n\nTime Used: {time_used} hour(s): {time_amount:,} VND"

        # Add total
        invoice_text += f"\n\nTOTAL: {total_amount:,} VND"

        # Show invoice
        msg_box = QMessageBox(self.mainWindow)
        msg_box.setWindowTitle("Invoice")
        msg_box.setText(invoice_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2A2F4F;
                color: #FDE2F3;
            }
            QLabel {
                color: #FDE2F3;
            }
            QPushButton {
                background-color: #917FB3;
                color: #FDE2F3;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E5BEEC;
                color: #2A2F4F;
            }
        """)
        
        msg_box.exec()

    def remove_menu_item(self, index):
        """Xóa món ăn khi double click vào hàng trong bảng"""
        # Lấy tên món ăn từ cột đầu tiên của hàng được chọn
        item_name = self.tableOrderMenu.item(index.row(), 1).text()
        
        # Hiển thị hộp thoại xác nhận
        msg_box = QMessageBox(self.mainWindow)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setText(f"Are you sure to delete {item_name}?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2A2F4F;
                color: #FDE2F3;
            }
            QLabel {
                color: #FDE2F3;
            }
            QPushButton {
                background-color: #917FB3;
                color: #FDE2F3;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E5BEEC;
                color: #2A2F4F;
            }
        """)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa món ăn khỏi dictionary
            if item_name in self.menu_items:
                del self.menu_items[item_name]
                # Cập nhật lại bảng
                self.update_order_table()

    def remove_selected_item(self):
        """Xóa món ăn đã chọn trong bảng"""
        # Lấy hàng đang được chọn
        selected_items = self.tableOrderMenu.selectedItems()
        if not selected_items:
            # Hiển thị thông báo
            msg_box = QMessageBox(self.mainWindow)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please select the food item to delete")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QLabel {
                    color: #FDE2F3;
                }
                QPushButton {
                    background-color: #917FB3;
                    color: #FDE2F3;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #E5BEEC;
                    color: #2A2F4F;
                }
            """)
            
            msg_box.exec()
            return
        
        # Lấy hàng đang được chọn (lấy item đầu tiên trong danh sách)
        row = selected_items[0].row()
        # Lấy tên món ăn từ cột đầu tiên
        item_name = self.tableOrderMenu.item(row, 1).text()
        
        # Hiển thị hộp thoại xác nhận
        msg_box = QMessageBox(self.mainWindow)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setText(f"Are you sure to delete {item_name}?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2A2F4F;
                color: #FDE2F3;
            }
            QLabel {
                color: #FDE2F3;
            }
            QPushButton {
                background-color: #917FB3;
                color: #FDE2F3;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E5BEEC;
                color: #2A2F4F;
            }
        """)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Xóa món ăn khỏi dictionary
            if item_name in self.menu_items:
                del self.menu_items[item_name]
                # Cập nhật lại bảng
                self.update_order_table()

    def exit_application(self):
        """Đăng xuất và quay lại màn hình đăng nhập"""
        # Show confirmation dialog first
        msg_box = QMessageBox(self.mainWindow)
        msg_box.setWindowTitle("Logout confirmation")
        msg_box.setText("Are you sure to log out?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2A2F4F;
                color: #FDE2F3;
            }
            QLabel {
                color: #FDE2F3;
            }
            QPushButton {
                background-color: #917FB3;
                color: #FDE2F3;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E5BEEC;
                color: #2A2F4F;
            }
        """)

        reply = msg_box.exec()

        # Only proceed to login screen if user confirmed
        if reply == QMessageBox.StandardButton.Yes:
            from ui.ui_ext_files.login_screen_ext import login_screen_ext

            self.mainWindow.hide()
            self.login_window = QMainWindow()
            self.login_screen = login_screen_ext()
            self.login_screen.setupUi(self.login_window)
            self.login_screen.showWindow()

    def reset_form(self):
        """Reset the form for a new order"""
        # Clear customer information
        self.lineEditTenKH.clear()
        self.lineEditSoKH.clear()
        
        # Clear server information
        self.lineEditServerMay.clear()
        self.lineEditServerID.clear()  # Clear Server ID field
        
        # Reset time used
        self.spinBoxThoiGianSuDung.setValue(0)
        
        # Clear menu items
        self.menu_items = {}
        self.update_order_table()
        
        # Generate new invoice ID
        self.generate_invoice_id()
        
        # Reset datetime
        self.setup_datetime()