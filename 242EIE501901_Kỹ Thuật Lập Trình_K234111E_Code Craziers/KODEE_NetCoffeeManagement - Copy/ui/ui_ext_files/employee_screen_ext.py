from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
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
        self.menu_items = {}
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
        self.current_employee = employee
        if employee:
            employee_info = f"Signed in as: Employee - {employee['name']} ({employee['id']})"
            self.label_EmployeeInfo.setText(employee_info)

    def showWindow(self):
        self.mainWindow.show()

    def setup_order_table(self):
        # Create table widget
        self.tableOrderMenu = QTableWidget(self.groupBoxOrderMenu)
        self.tableOrderMenu.setColumnCount(4)
        self.tableOrderMenu.setHorizontalHeaderLabels(["Name of dish", "Quantity", "Price", "Total amount"])

        # Set table properties
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tableOrderMenu.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Create a layout for the Order Menu groupbox if it doesn't exist
        if self.groupBoxOrderMenu.layout() is None:
            layout = QtWidgets.QVBoxLayout(self.groupBoxOrderMenu)
            self.groupBoxOrderMenu.setLayout(layout)

        # Add table to the Order Menu groupbox
        self.groupBoxOrderMenu.layout().addWidget(self.tableOrderMenu)

    def connect_menu_buttons(self):
        """Connect all menu buttons to the add_menu_item function"""
        # Get all buttons in the Menu tab
        for i in range(1, 31):  # Assuming there are 30 menu buttons
            button_name = f"ButtonMenu{i}"
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.clicked.connect(self.add_menu_item)

    def filter_servers(self, checked=None):
        if checked is False and not hasattr(self, 'server_manager'):
            return
            
        if not self.server_manager:
            return
        if self.radioButtonAvailable.isChecked():
            servers = self.server_manager.get_available_servers()
        elif self.radioButton_Unavailable.isChecked():
            servers = self.server_manager.get_occupied_servers()
        else:
            servers = self.server_manager.get_all_servers()
        self.update_server_buttons(servers)

    def update_server_buttons(self, filtered_servers=None):
        if not self.server_manager:
            return

        if filtered_servers is None:
            filtered_servers = self.server_manager.get_all_servers()

        server_dict = {server.id: server for server in filtered_servers}

        for i in range(1, 31):  #Suppose there are 30 node servers
            button_name = f"ButtonMay{i}"
            server_id = f"SE{i:02d}"
            
            if hasattr(self, button_name):
                button = getattr(self, button_name)

                if server_id in server_dict:
                    button.show()
                    server = server_dict[server_id]

                    if server.status == "available":
                        # Purple for empty server
                        button.setStyleSheet("background-color: rgb(229, 190, 236);")
                    else:
                        # Red for server in use
                        button.setStyleSheet("background-color: rgb(255, 0, 0);")
                else:
                    # Hide button if server is not in filter list
                    button.hide()

    def connect_server_buttons(self):

        for i in range(1, 31):  # Assuming there are 30 server buttons
            button_name = f"ButtonMay{i}"
            if hasattr(self, button_name):
                button = getattr(self, button_name)
                button.clicked.connect(self.select_server)
        
        # Update the status of the initial server nodes
        self.update_server_buttons()

    def add_menu_item(self):
        """Add a menu item to the order table when a menu button is clicked"""
        # Get the sender button
        button = self.mainWindow.sender()
        if not button:
            return
        try:
            #Get button information
            button_name = button.objectName()
            button_text = button.text().strip()
            button_tooltip = button.toolTip().strip() if button.toolTip() else ""
            
            #Find food information from multiple sources
            item_info = None
            price_k = None
            
            #Show debug information to find the problem
            debug_info = f"Button name: {button_name}\nButton text: {button_text}\nTooltip: {button_tooltip}\n"
            
            #Method 1: Look in the tooltip (if any)
            if button_tooltip:
                # Suppose the tooltip can contain the information "Item Name: X, Price: Y"
                item_match = re.search(r"Item:\s*(.*?),", button_tooltip)
                price_match = re.search(r"Price:\s*(\d+)", button_tooltip)
                
                if item_match and price_match:
                    item_info = item_match.group(1).strip()
                    price_k = int(price_match.group(1))
                    debug_info += f"Found from tooltip: {item_info}, {price_k}k\n"
            
            #Method 2: Find from the button ID number
            if not item_info and re.match(r"ButtonMenu(\d+)", button_name):
                button_id = re.match(r"ButtonMenu(\d+)", button_name).group(1)
                
                #Get data from dataset menu_items.json
                current_file = os.path.abspath(__file__)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                dataset_path = os.path.join(project_root, 'dataset')
                menu_items_path = os.path.join(dataset_path, 'menu_items.json')
                
                if os.path.exists(menu_items_path):
                    with open(menu_items_path, 'r', encoding='utf-8') as f:
                        menu_data = json.load(f)
                    
                    #Get the dish corresponding to the button_id (assuming the order in the file matches the order of the button)
                    button_index = int(button_id) - 1
                    if 0 <= button_index < len(menu_data):
                        menu_item = menu_data[button_index]
                        item_info = menu_item.get('name', '')
                        price_k = menu_item.get('price', 0) // 1000  # Convert from VND to k
                        debug_info += f"Found from dataset: {item_info}, {price_k}k\n"
            
            #Method 3: Fix some sample values for testing purposes
            if not item_info:
                # Create a sample menu list
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
                
                # Get a random dish from the sample list
                import random
                sample_item = random.choice(sample_menu)
                item_info = sample_item["name"]
                price_k = sample_item["price"] // 1000
                debug_info += f"Using sample item: {item_info}, {price_k}k\n"
            
            # If the dish information is still not found, display a message and exit.
            if not item_info or not price_k:
                # Display debug information to help find errors
                QMessageBox.warning(self.mainWindow, "Debug Information", debug_info)
                QMessageBox.warning(self.mainWindow, "Error", "Unable to read dish information. Please view debug information.")
                return
            
            #Calculate price from k to VND
            price = price_k * 1000
                
            #Update menu_items dictionary
            if item_info in self.menu_items:
                self.menu_items[item_info]["quantity"] += 1
            else:
                self.menu_items[item_info] = {
                    "price": price,
                    "quantity": 1
                }
            
            #Update table
            self.update_order_table()
            
        except Exception as e:
            # Show detailed errors for easy debugging
            error_message = f"Error processing food information: {str(e)}\n"
            error_message += f"Button name: {button.objectName() if button else 'Unknown'}\n"
            error_message += f"Button text: {button.text() if button else 'Unknown'}"
            
            QMessageBox.warning(self.mainWindow, "Error", error_message)
            return

    def update_order_table(self):
        """Update the order table with the current menu items"""
        # Clear the table
        self.tableOrderMenu.setRowCount(0)

        # Add items to the table
        row = 0
        for item_name, details in self.menu_items.items():
            self.tableOrderMenu.insertRow(row)

            # Item name
            self.tableOrderMenu.setItem(row, 0, QTableWidgetItem(item_name))

            # Quantity
            quantity = details["quantity"]
            self.tableOrderMenu.setItem(row, 1, QTableWidgetItem(str(quantity)))

            # Price
            price = details["price"]
            self.tableOrderMenu.setItem(row, 2, QTableWidgetItem(f"{price:,} VND"))

            # Total
            total = price * quantity
            self.tableOrderMenu.setItem(row, 3, QTableWidgetItem(f"{total:,} VND"))

            row += 1
        
        #Update total amount
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
            QMessageBox.warning(self.mainWindow, "Error", "Invalid server format")
            return

        server_number = match.group(1)
        server_id = f"SE{int(server_number):02d}"
        
        # Kiểm tra trạng thái server
        server = self.server_manager.get_server_by_id(server_id)
        if not server:
            QMessageBox.warning(self.mainWindow, "Error", f"Cannot find server {server_id}")
            return
        
        if not server.is_available():
            QMessageBox.warning(self.mainWindow, "Error", f"Server {server_id} is being used")
            return
        
        # Lưu server hiện tại
        self.current_server = server
        
        # Set the server number in the line edit
        self.lineEditServerMay.setText(server_id)
        
        # Đổi màu nút server đang chọn sang màu trắng
        button.setStyleSheet("background-color: rgb(255, 255, 255);")

    def generate_invoice_id(self):
        """Generate a random invoice ID in the format KDxxxxx"""
        # Generate 5 random digits
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        invoice_id = f"KD{random_digits}"

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
        # Check if required fields are filled
        if not self.lineEditTenKH.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please enter customer name")
            return

        if not self.lineEditSoKH.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please enter phone number")
            return

        if not self.lineEditServerMay.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please select a server")
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

        # Show confirmation message
        QMessageBox.information(
            self.mainWindow,
            "Payment Confirmation",
            f"Total amount: {total_amount:,} VND\nPayment confirmed successfully!"
        )

    def generate_invoice(self):
        """Generate and display an invoice"""
        # Check if required fields are filled
        if not self.lineEditTenKH.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please enter customer name")
            return

        if not self.lineEditSoKH.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please enter phone number")
            return

        if not self.lineEditServerMay.text():
            QMessageBox.warning(self.mainWindow, "Warning", "Please select a server")
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
        QMessageBox.information(self.mainWindow, "Invoice", invoice_text)

    def exit_application(self):
        """Exit the application"""
        reply = QMessageBox.question(
            self.mainWindow,
            "Log Out Confirmation",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()