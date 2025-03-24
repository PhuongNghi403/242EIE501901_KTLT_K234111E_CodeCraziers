from ui.ui_files.manager_screen import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
import os
import json
import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from dataset.classes_readjson import load_employees, load_managers, load_menu_items, load_shifts, load_invoices

class manager_screen_ext(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.current_manager = None
        
        # Điều chỉnh đường dẫn đến thư mục chứa dữ liệu JSON
        current_file = os.path.abspath(__file__)
        # Đi lên 3 cấp: ui/ui_ext_files -> ui -> project_root
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        self.dataset_path = os.path.join(self.project_root, 'dataset')
        
        # Thêm các biến để quản lý dữ liệu
        self.employees = []
        self.managers = []
        self.menu_items = []
        self.shifts = []
        self.invoices = []
        
        # Kết nối các sự kiện tab changed
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        
        # Kết nối các sự kiện
        self.pushButtonLogOut.clicked.connect(self.logout)
        
        # Kết nối các nút trong tab Quản lý Menu
        self.pushButton_AddItem_3.clicked.connect(self.add_menu_item)
        self.pushButton_DeleteItem_3.clicked.connect(self.delete_menu_item)
        self.pushButton_EditItem_2.clicked.connect(self.edit_menu_item)
        self.comboBox_Category_2.currentIndexChanged.connect(self.filter_menu_items)
        
        # Kết nối các nút trong tab Quản lý Ca làm
        self.pushButton_AddDetail_2.clicked.connect(self.add_shift)
        self.pushButton_DeleteDetail_2.clicked.connect(self.delete_shift)
        
        # Sửa lỗi: QDateEdit không có currentIndexChanged, phải dùng dateChanged
        self.dateEdit_WorkingDayFilter_2.dateChanged.connect(self.filter_shifts)
        self.comboBox_ShiftFilter_2.currentIndexChanged.connect(self.filter_shifts)

        # Kết nối các nút trong tab Quản lý Hóa đơn
        self.comboBox_ItemFilter_2.currentIndexChanged.connect(self.filter_invoices)
        self.tableWidget_ItemDetailsList_2.itemClicked.connect(self.show_invoice_details)
        
        # Tải dữ liệu lần đầu
        self.load_data()
        
        # Hiển thị dashboard mặc định khi mở
        self.tabWidget.setCurrentIndex(0)
        self.update_dashboard()
        
    def load_data(self):
        """Tải dữ liệu từ các file JSON"""
        # Đổi directory để đọc file JSON
        os.chdir(self.dataset_path)
        
        # Đọc dữ liệu từ các file JSON
        self.employees = load_employees()
        self.managers = load_managers() 
        self.menu_items = load_menu_items()
        self.shifts = load_shifts()
        self.invoices = load_invoices()
        
    def on_tab_changed(self, index):
        """Xử lý khi chuyển tab"""
        # Tải lại dữ liệu khi chuyển tab
        self.load_data()
        
        # Cập nhật giao diện dựa trên tab được chọn
        if index == 0:  # Tab Dashboard
            self.update_dashboard()
        elif index == 1:  # Tab Quản lý Menu
            self.update_menu_table()
        elif index == 2:  # Tab Quản lý Ca làm
            self.update_shift_table()
        elif index == 3:  # Tab Quản lý Hóa đơn
            self.update_invoice_table()
        
    def set_current_manager(self, manager):
        """Đặt thông tin quản lý hiện tại và hiển thị trên giao diện"""
        self.current_manager = manager
        if manager:
            # Hiển thị thông tin quản lý đăng nhập ở label_ManagerInfo
            manager_info = f"Signed in as: Manager - {manager['name']} ({manager['id']})"
            self.label_ManagerInfo_2.setText(manager_info)
    
    def showWindow(self):
        """Hiển thị cửa sổ quản lý"""
        self.MainWindow.show()
        
    def logout(self):
        """Đăng xuất và quay lại màn hình đăng nhập"""
        from ui.ui_ext_files.login_screen_ext import login_screen_ext
        
        self.MainWindow.hide()
        self.login_window = QMainWindow()
        self.login_screen = login_screen_ext()
        self.login_screen.setupUi(self.login_window)
        self.login_screen.showWindow()
    
    #======================= DASHBOARD =======================
    def update_dashboard(self):
        """Cập nhật tab Dashboard với dữ liệu thống kê"""
        # Tính toán thống kê
        total_revenue = sum(invoice['total'] for invoice in self.invoices)
        total_employees = len(self.employees)
        total_menu_items = len(self.menu_items)
        total_invoices = len(self.invoices)
        
        # Hiển thị thông tin tổng quan
        self.label_Revenue.setText(f"{total_revenue:,} VND")
        self.label_TotalEmployees.setText(str(total_employees))
        self.label_TotalMenuItems.setText(str(total_menu_items))
        self.label_TotalInvoices.setText(str(total_invoices))
        
        # Vẽ biểu đồ thống kê
        self.draw_revenue_chart()
        self.draw_top_menu_chart()
    
    def draw_revenue_chart(self):
        """Vẽ biểu đồ doanh thu theo buổi (Sáng/Chiều/Tối)"""
        # Xóa biểu đồ cũ nếu có
        if hasattr(self, 'revenue_canvas'):
            self.groupBoxRevenueChart.layout().removeWidget(self.revenue_canvas)
            self.revenue_canvas.deleteLater()
        
        # Tạo figure mới
        revenue_figure = Figure(figsize=(5, 4), dpi=100)
        revenue_canvas = FigureCanvas(revenue_figure)
        self.revenue_canvas = revenue_canvas
        
        # Thêm canvas vào frame
        if self.groupBoxRevenueChart.layout() is None:
            # Tạo layout mới nếu chưa có
            from PyQt6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.groupBoxRevenueChart)
            self.groupBoxRevenueChart.setLayout(layout)
        else:
            layout = self.groupBoxRevenueChart.layout()
        layout.addWidget(revenue_canvas)
        
        # Tính toán doanh thu theo buổi
        morning_revenue = 0
        afternoon_revenue = 0
        evening_revenue = 0
        
        for invoice in self.invoices:
            # Kiểm tra thời gian để phân loại buổi
            time_in = invoice.get('time_in', '12:00')
            hour = int(time_in.split(':')[0])
            
            if 6 <= hour < 12:  # Buổi sáng: 6h-12h
                morning_revenue += invoice['total']
            elif 12 <= hour < 18:  # Buổi chiều: 12h-18h
                afternoon_revenue += invoice['total']
            else:  # Buổi tối: 18h-6h
                evening_revenue += invoice['total']
        
        # Dữ liệu cho biểu đồ
        shifts = ['Morning', 'Afternoon', 'Evening']
        revenues = [morning_revenue, afternoon_revenue, evening_revenue]
        
        # Vẽ biểu đồ đường
        ax = revenue_figure.add_subplot(111)
        ax.plot(shifts, revenues, 'o-', linewidth=2, markersize=8)
        ax.set_title('Revenue per session')
        ax.set_ylabel('Revenue (VND)')
        
        # Thêm nhãn giá trị
        for i, revenue in enumerate(revenues):
            ax.annotate(f"{revenue:,}", (i, revenue), textcoords="offset points", 
                        xytext=(0, 10), ha='center')
        
        # Cập nhật canvas
        revenue_canvas.draw()
    
    def draw_top_menu_chart(self):
        """Vẽ biểu đồ top 3 món ăn bán chạy nhất"""
        # Xóa biểu đồ cũ nếu có
        if hasattr(self, 'menu_canvas'):
            self.groupBoxTop3Chart.layout().removeWidget(self.menu_canvas)
            self.menu_canvas.deleteLater()
        
        # Tạo figure mới
        menu_figure = Figure(figsize=(5, 4), dpi=100)
        menu_canvas = FigureCanvas(menu_figure)
        self.menu_canvas = menu_canvas
        
        # Thêm canvas vào frame
        if self.groupBoxTop3Chart.layout() is None:
            # Tạo layout mới nếu chưa có
            from PyQt6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self.groupBoxTop3Chart)
            self.groupBoxTop3Chart.setLayout(layout)
        else:
            layout = self.groupBoxTop3Chart.layout()
        layout.addWidget(menu_canvas)
        
        # Tính toán số lượng bán của từng món
        menu_counter = {}
        
        for invoice in self.invoices:
            for item in invoice['order']['items']:
                item_name = item['name']
                quantity = item['quantity']
                
                if item_name in menu_counter:
                    menu_counter[item_name] += quantity
                else:
                    menu_counter[item_name] = quantity
        
        # Lấy top 3 món bán chạy nhất
        top_items = sorted(menu_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Tổng số lượng của top 3
        top_total = sum(count for _, count in top_items)
        
        # Dữ liệu cho biểu đồ
        labels = [item for item, _ in top_items]
        sizes = [count for _, count in top_items]
        
        # Vẽ biểu đồ tròn
        ax = menu_figure.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_title('Top 3 best selling dishes')
        
        # Cập nhật canvas
        menu_canvas.draw()
    
    #======================= QUẢN LÝ MENU =======================
    def update_menu_table(self):
        """Cập nhật bảng danh sách món ăn"""
        # Xóa dữ liệu cũ
        self.tableWidget_MenuItemsList_2.setRowCount(0)
        
        # Lọc dữ liệu theo loại món
        selected_category = self.comboBox_Category_2.currentText()
        filtered_items = self.menu_items
        
        if selected_category != "All":
            filtered_items = [item for item in self.menu_items 
                             if item['category'].lower() == selected_category.lower()]
        
        # Thêm dữ liệu vào bảng
        self.tableWidget_MenuItemsList_2.setRowCount(len(filtered_items))
        
        for row, item in enumerate(filtered_items):
            # Mã món
            self.tableWidget_MenuItemsList_2.setItem(row, 0, QTableWidgetItem(item['id']))
            # Tên món
            self.tableWidget_MenuItemsList_2.setItem(row, 1, QTableWidgetItem(item['name']))
            # Giá
            price_item = QTableWidgetItem(f"{item['price']:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tableWidget_MenuItemsList_2.setItem(row, 2, price_item)
            # Loại
            self.tableWidget_MenuItemsList_2.setItem(row, 3, QTableWidgetItem(item['category']))
        
        # Điều chỉnh chiều rộng cột
        self.tableWidget_MenuItemsList_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    
    def filter_menu_items(self):
        """Lọc danh sách món ăn theo loại"""
        self.update_menu_table()
    
    def add_menu_item(self):
        """Thêm món ăn mới"""
        # Lấy thông tin từ các trường nhập liệu
        item_id = self.lineEdit_ItemID_2.text().strip()
        item_name = self.lineEdit_ItemName_3.text().strip()
        
        try:
            price = int(self.spinBox_Price_3.text().strip().replace(',', ''))
        except ValueError:
            QMessageBox.warning(self.MainWindow, "Error", "Invalid price")
            return
        
        category = self.comboBox_Category_2.currentText()
        
        # Kiểm tra dữ liệu đầu vào
        if not item_id or not item_name or price <= 0:
            QMessageBox.warning(self.MainWindow, "Error", "Please enter complete information")
            return
        
        # Kiểm tra mã món đã tồn tại chưa
        for item in self.menu_items:
            if item['id'] == item_id:
                QMessageBox.warning(self.MainWindow, "Error", f"Item code {item_id} already exists")

                return
        
        # Add new díhs
        new_item = {
            'id': item_id,
            'name': item_name,
            'price': price,
            'category': category,
            'order_count': 0
        }
        
        # Add to list
        self.menu_items.append(new_item)
        
        # Save in file JSON
        self.save_menu_items()
        
        # Update table
        self.update_menu_table()
        
        # Clear input data
        self.lineEdit_ItemID_2.clear()
        self.lineEdit_ItemName_3.clear()
        self.spinBox_Price_3.clear()
        
        # Notification successful
        QMessageBox.information(self.MainWindow, "Notification", "Add item successfully")
    
    def edit_menu_item(self):
        """Edit the dish"""
        #Check if any row is selected
        selected_rows = self.tableWidget_MenuItemsList_2.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self.MainWindow, "Error", "Please select the item you want to edit")
            return
        
        # Get the item code of the selected item
        row = selected_rows[0].row()
        item_id = self.tableWidget_MenuItemsList_2.item(row, 0).text()
        
        # Get information from input fields
        new_name = self.lineEdit_ItemName_3.text().strip()
        
        try:
            new_price = int(self.spinBox_Price_3.text().strip().replace(',', ''))
        except ValueError:
            QMessageBox.warning(self.MainWindow, "Error", "Invalid price")
            return

        new_category = self.comboBox_Category_2.currentText()

        # Check input data
        if not new_name or new_price <= 0:
            QMessageBox.warning(self.MainWindow, "Error", "Please enter complete information")
            return
        
        #Find and update dishes
        for item in self.menu_items:
            if item['id'] == item_id:
                item['name'] = new_name
                item['price'] = new_price
                item['category'] = new_category
                break
        
        #Save to JSON file
        self.save_menu_items()
        
        #Update table
        self.update_menu_table()
        
        #  Clear input data
        self.lineEdit_ItemID_2.clear()
        self.lineEdit_ItemName_3.clear()
        self.spinBox_Price_3.clear()
        
        # Notification successful
        QMessageBox.information(self.MainWindow, "Notification", "Update successful")
    
    def delete_menu_item(self):
        """Delete the dish"""
        # Check if any row is selected
        selected_rows = self.tableWidget_MenuItemsList_2.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self.MainWindow, "Error", "Please select the item to delete")
            return
        
        #Get the item code of the selected item
        row = selected_rows[0].row()
        item_id = self.tableWidget_MenuItemsList_2.item(row, 0).text()
        item_name = self.tableWidget_MenuItemsList_2.item(row, 1).text()
        
        #Show confirmation alert
        reply = QMessageBox.question(
            self.MainWindow,
            "Delete confirm",
            f"Are you sure you want to delete item '{item_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove dish from list
            self.menu_items = [item for item in self.menu_items if item['id'] != item_id]
            
            #Save to JSON file
            self.save_menu_items()
            
            #Update table
            self.update_menu_table()
            
            #Clear input data
            QMessageBox.information(self.MainWindow, "Notification", "Delete successful")
    
    def save_menu_items(self):
        """Save the list of dishes to a JSON file"""
        menu_items_path = os.path.join(self.dataset_path, 'menu_items.json')
        
        with open(menu_items_path, 'w', encoding='utf-8') as f:
            json.dump(self.menu_items, f, ensure_ascii=False, indent=4)
    
    #======================= SHIFT MANAGEMENT =======================
    def update_shift_table(self):
        """Update shift list"""
        # Delete old data
        self.tableWidget_WorkdayList_2.setRowCount(0)

        # Get the selected date value from dateEdit
        selected_date = self.dateEdit_WorkingDayFilter_2.date()
        selected_month = selected_date.month()
        selected_shift = self.comboBox_ShiftFilter_2.currentText()
        
        filtered_shifts = self.shifts
        
        # Filter by month if date is selected
        if selected_month > 0:
            filtered_shifts = [shift for shift in filtered_shifts 
                              if datetime.datetime.strptime(shift['date'], "%Y-%m-%d").month == selected_month]
        
        #Filter by case type if not "All"
        if selected_shift != "All":
            filtered_shifts = [shift for shift in filtered_shifts 
                              if shift['name'] == selected_shift]
        
        #Add data to the table
        self.tableWidget_WorkdayList_2.setRowCount(len(filtered_shifts))

        for row, shift in enumerate(filtered_shifts):
            self.tableWidget_WorkdayList_2.setItem(row, 0, QTableWidgetItem(shift['id']))
            self.tableWidget_WorkdayList_2.setItem(row, 1, QTableWidgetItem(shift['name']))
            self.tableWidget_WorkdayList_2.setItem(row, 2, QTableWidgetItem(shift['employee_id']))
            self.tableWidget_WorkdayList_2.setItem(row, 3, QTableWidgetItem(shift['employee_name']))
            self.tableWidget_WorkdayList_2.setItem(row, 4, QTableWidgetItem(shift['date']))
        
        # Adjust column width
        self.tableWidget_WorkdayList_2.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_WorkdayList_2.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
    
    def filter_shifts(self):
        """Filter shift list"""
        self.update_shift_table()
    
    def add_shift(self):
        """Add new shift"""
        # Get information from input fields
        shift_id = self.lineEdit_ShiftID_2.text().strip()
        shift_name = self.comboBox_ShiftName_2.currentText()
        employee_id = self.lineEdit_EmployeeID_3.text().strip()
        shift_date = self.dateEdit_WorkingDay_2.date().toString("yyyy-MM-dd")
        
        # Check input data
        if not shift_id or not employee_id:
            QMessageBox.warning(self.MainWindow, "Error", "Please enter complete information")
            return
        
        #Check if the shift code already exists
        for shift in self.shifts:
            if shift['id'] == shift_id:
                QMessageBox.warning(self.MainWindow, "Error", f"Shift code {shift_id} already exists")
                return
        
        #Check if employee exists
        employee_name = ""
        for employee in self.employees:
            if employee['id'] == employee_id:
                employee_name = employee['name']
                break
        
        if not employee_name:
            QMessageBox.warning(self.MainWindow, "Error", f"Employee with code {employee_id} does not exist")
            return
        
        #Create new shift
        new_shift = {
            'id': shift_id,
            'name': shift_name,
            'employee_id': employee_id,
            'employee_name': employee_name,
            'date': shift_date
        }
        
        # Add to list
        self.shifts.append(new_shift)
        
        # Save in Json file
        self.save_shifts()
        
        # Table Update
        self.update_shift_table()
        
        # Clear Input data
        self.lineEdit_ShiftID_2.clear()
        self.lineEdit_EmployeeID_3.clear()
        
        # Notification successful
        QMessageBox.information(self.MainWindow, "Notification", "Add successful shift")
    
    def delete_shift(self):
        """Delete shift"""
        # Check if any row is selected
        selected_rows = self.tableWidget_WorkdayList_2.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self.MainWindow, "Error", "Please select the shift to delete")
            return
        
        # Get the shift code of the selected item
        row = selected_rows[0].row()
        shift_id = self.tableWidget_WorkdayList_2.item(row, 0).text()
        shift_name = self.tableWidget_WorkdayList_2.item(row, 1).text()
        shift_date = self.tableWidget_WorkdayList_2.item(row, 4).text()
        
        # Show confirmation alert
        reply = QMessageBox.question(
            self.MainWindow,
            "Confirm deletion",
            f"Are you sure you want to delete shift '{shift_name}' on {shift_date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove shift from list
            self.shifts = [shift for shift in self.shifts if shift['id'] != shift_id]
            
            #Save in Json file
            self.save_shifts()
            
            #Table Update
            self.update_shift_table()
            
            # Notification successful
            QMessageBox.information(self.MainWindow, "Notification", "Delete shift successfully")
    
    def save_shifts(self):
        """Save shift list to JSON file"""
        shifts_path = os.path.join(self.dataset_path, 'shifts.json')
        
        with open(shifts_path, 'w', encoding='utf-8') as f:
            json.dump(self.shifts, f, ensure_ascii=False, indent=4)
    
    #======================= BILLING MANAGEMENT =======================
    def update_invoice_table(self):
        """Update invoice list"""
        # Delete old data
        self.tableWidget_InvoiceList_3.setRowCount(0)
        
        # Filter data by month
        # Bug fix: instead of calling currentText() on dateEdit, get the date value
        selected_date = self.dateEdit_DateFilter_3.date()
        selected_month = selected_date.month()
        
        filtered_invoices = self.invoices
        
        # Filter by month if date is selected
        if selected_month > 0:
            filtered_invoices = [invoice for invoice in filtered_invoices 
                                if datetime.datetime.strptime(invoice['date'], "%Y-%m-%d").month == selected_month]
        
        # Add data to the table
        self.tableWidget_InvoiceList_3.setRowCount(len(filtered_invoices))
        
        for row, invoice in enumerate(filtered_invoices):
            self.tableWidget_InvoiceList_3.setItem(row, 0, QTableWidgetItem(invoice['id']))
            self.tableWidget_InvoiceList_3.setItem(row, 1, QTableWidgetItem(invoice['date']))
            self.tableWidget_InvoiceList_3.setItem(row, 2, QTableWidgetItem(invoice['time_in']))
            self.tableWidget_InvoiceList_3.setItem(row, 3, QTableWidgetItem(invoice['time_out']))
            self.tableWidget_InvoiceList_3.setItem(row, 4, QTableWidgetItem(invoice['order']['customer_name']))
            total_item = QTableWidgetItem(f"{invoice['total']:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tableWidget_InvoiceList_3.setItem(row, 5, total_item)
            # Save invoice data to display details
            self.tableWidget_InvoiceList_3.setItem(row, 6, QTableWidgetItem(str(row)))
        
        # Hide column containing index
        self.tableWidget_InvoiceList_3.hideColumn(6)
        
        # Adjust column width
        self.tableWidget_InvoiceList_3.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_InvoiceList_3.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        #Delete old data in the detail table
        self.tableWidget_ItemDetailsList_2.setRowCount(0)
    
    def filter_invoices(self):
        """Filter invoice list"""
        self.update_invoice_table()
    
    def show_invoice_details(self, item):
        """Show invoice details when selecting an invoice in the table"""
        #Pick up selected items
        row = item.row()
        invoice_id = self.tableWidget_InvoiceList_3.item(row, 0).text()
        
        #Find the corresponding invoice
        selected_invoice = None
        for invoice in self.invoices:
            if invoice['id'] == invoice_id:
                selected_invoice = invoice
                break
        
        if not selected_invoice:
            return
        
        # Delete old data in the detail table
        self.tableWidget_ItemDetailsList_2.setRowCount(0)
        
        # More computer usage information
        usage_time = selected_invoice['order']['usage_time']
        usage_price = selected_invoice['order']['usage_price']
        
        self.tableWidget_ItemDetailsList_2.insertRow(0)
        self.tableWidget_ItemDetailsList_2.setItem(0, 0, QTableWidgetItem("SERVER"))
        self.tableWidget_ItemDetailsList_2.setItem(0, 1, QTableWidgetItem(f"Using the computer {selected_invoice['order']['computer_id']}"))
        self.tableWidget_ItemDetailsList_2.setItem(0, 2, QTableWidgetItem(str(usage_time)))
        
        price_item = QTableWidgetItem(f"{usage_price / usage_time:,}")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tableWidget_ItemDetailsList_2.setItem(0, 3, price_item)
        
        total_item = QTableWidgetItem(f"{usage_price:,}")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tableWidget_ItemDetailsList_2.setItem(0, 4, total_item)
        
        #Add dish information
        row = 1
        for item in selected_invoice['order']['items']:
            self.tableWidget_ItemDetailsList_2.insertRow(row)

            self.tableWidget_ItemDetailsList_2.setItem(row, 0, QTableWidgetItem(item.get('item_id', '')))
            self.tableWidget_ItemDetailsList_2.setItem(row, 1, QTableWidgetItem(item['name']))
            self.tableWidget_ItemDetailsList_2.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            price_item = QTableWidgetItem(f"{item['price']:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tableWidget_ItemDetailsList_2.setItem(row, 3, price_item)
            # Thành tiền
            total = item['price'] * item['quantity']
            total_item = QTableWidgetItem(f"{total:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tableWidget_ItemDetailsList_2.setItem(row, 4, total_item)
            
            row += 1
        
        # Adjust column width
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
