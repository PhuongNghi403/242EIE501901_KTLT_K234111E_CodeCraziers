from PyQt6 import QtWidgets, QtCore

from ui.ui_files.manager_screen import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QDate, QTimer
import sys
import os
import json
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from dataset.classes_readjson import load_employees, load_managers, load_menu_items, load_shifts, load_invoices
from PyQt6.QtGui import QFont, QColor


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

        # Thêm các loại món ăn vào comboBox Filter trong Menu Items List
        if self.comboBox_ShiftFilter_2.count() == 0:
            self.comboBox_ItemFilter_2.addItem("All")
            self.comboBox_ItemFilter_2.addItem("Food")
            self.comboBox_ItemFilter_2.addItem("Drink")
            self.comboBox_ItemFilter_2.addItem("Snack")

        # Thêm các loại ca làm vào comboBox Shift Filter
        if self.comboBox_ShiftFilter_2.count() == 0:
            self.comboBox_ShiftFilter_2.addItem("All")
            self.comboBox_ShiftFilter_2.addItem("Morning")
            self.comboBox_ShiftFilter_2.addItem("Afternoon")
            self.comboBox_ShiftFilter_2.addItem("Evening")

        # Thêm các loại ca làm vào comboBox Shift Name
        if self.comboBox_ShiftName_2.count() == 0:
            self.comboBox_ShiftName_2.addItem("Morning")
            self.comboBox_ShiftName_2.addItem("Afternoon")
            self.comboBox_ShiftName_2.addItem("Evening")

        # Thêm các loại món ăn vào comboBox Category trong Menu Items Details
        if self.comboBox_Category_2.count() == 0:
            self.comboBox_Category_2.addItem("Food")
            self.comboBox_Category_2.addItem("Drink")
            self.comboBox_Category_2.addItem("Snack")

        # Thiết lập định dạng hiển thị cho dateEdit Working Day
        self.dateEdit_WorkingDay_2.setDisplayFormat("dd/MM/yyyy")
        self.dateEdit_WorkingDayFilter_2.setDisplayFormat("dd/MM/yyyy")

        # Thiết lập dateEdit cho Working Day
        self.dateEdit_WorkingDay_2.setDisplayFormat("dd/MM/yyyy")
        self.dateEdit_WorkingDay_2.setCalendarPopup(True)  # Cho phép hiển thị lịch
        self.dateEdit_WorkingDay_2.setReadOnly(False)  # Cho phép chỉnh sửa trực tiếp
        self.dateEdit_WorkingDayFilter_2.setDisplayFormat("dd/MM/yyyy")
        self.dateEdit_WorkingDayFilter_2.setCalendarPopup(True)  # Cho phép hiển thị lịch
        self.dateEdit_WorkingDayFilter_2.setReadOnly(False)  # Cho phép chỉnh sửa trực tiếp

        # Thiết lập dateEdit cho Invoice Management
        self.dateEdit_PaymentDate_2.setDisplayFormat("dd/MM/yyyy")
        self.dateEdit_PaymentDate_2.setCalendarPopup(True)  # Cho phép hiển thị lịch
        self.dateEdit_PaymentDate_2.setReadOnly(False)  # Cho phép chỉnh sửa trực tiếp
        self.dateEdit_DateFilter_3.setDisplayFormat("dd/MM/yyyy")
        self.dateEdit_DateFilter_3.setCalendarPopup(True)  # Cho phép hiển thị lịch
        self.dateEdit_DateFilter_3.setReadOnly(False)  # Cho phép chỉnh sửa trực tiếp

        # Kết nối các sự kiện tab changed
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # Kết nối các sự kiện
        self.pushButtonLogOut.clicked.connect(self.logout)

        # Kết nối các nút trong tab Quản lý Menu
        self.pushButton_AddItem_3.clicked.connect(self.add_menu_item)
        self.pushButton_DeleteItem_3.clicked.connect(self.delete_menu_item)
        self.pushButton_EditItem_2.clicked.connect(self.edit_menu_item)
        self.pushButton_SaveItem_3.clicked.connect(self.save_menu_item_details)

        # Kết nối sự kiện lọc món ăn theo comboBox Filter trong Menu Items List
        self.comboBox_ItemFilter_2.currentIndexChanged.connect(self.filter_menu_items)

        # Kết nối sự kiện chọn item trong bảng menu
        self.tableWidget_MenuItemsList_2.itemClicked.connect(self.select_menu_item)

        # Điều chỉnh giới hạn giá tiền cho spinBox_Price_3
        self.spinBox_Price_3.setMaximum(1000000)
        self.spinBox_Price_3.setSingleStep(1000)

        # Điều chỉnh giới hạn giá tiền cho spinBox_TotalPayment_2
        self.spinBox_TotalPayment_2.setMaximum(100000000)
        self.spinBox_TotalPayment_2.setSingleStep(1000)

        # Kết nối các nút trong tab Quản lý Ca làm
        self.pushButton_AddDetail_2.clicked.connect(self.add_shift)
        self.pushButton_DeleteDetail_2.clicked.connect(self.delete_shift)
        self.pushButton_ClearFilter_3.clicked.connect(self.clear_shift_filter)

        # Kết nối sự kiện lọc ca làm
        self.dateEdit_WorkingDayFilter_2.dateChanged.connect(self.filter_shifts)
        self.comboBox_ShiftFilter_2.currentIndexChanged.connect(self.filter_shifts)

        # Kết nối các nút trong tab Quản lý Hóa đơn
        self.pushButton_DeleteInvoice_2.clicked.connect(self.delete_invoice)
        self.pushButton_AddInvoice_2.clicked.connect(self.add_invoice)
        self.pushButton_ClearFilter_5.clicked.connect(self.clear_invoice_filter)

        # Kết nối sự kiện chọn invoice trong bảng
        self.tableWidget_InvoiceList_3.itemClicked.connect(self.select_invoice)

        # Kết nối sự kiện lọc hóa đơn theo tháng
        self.dateEdit_DateFilter_3.dateChanged.connect(self.filter_invoices)

        # Kết nối sự kiện khi ngày thay đổi
        self.dateEdit_WorkingDay_2.dateChanged.connect(self.on_working_day_changed)

        # Kết nối sự kiện chọn workday trong bảng
        self.tableWidget_WorkdayList_2.itemClicked.connect(self.select_workday)
        self.dateEdit_WorkingDayFilter_2.dateChanged.connect(self.filter_shifts)
        self.comboBox_ShiftFilter_2.currentIndexChanged.connect(self.filter_shifts)

        # Tải dữ liệu lần đầu
        self.load_data()

        # Thêm dữ liệu mẫu cho Drink và Snack nếu chưa có
        self.add_sample_drink_snack_items()

        # Hiển thị dashboard mặc định khi mở
        self.tabWidget.setCurrentIndex(0)
        self.update_dashboard()

        # Cập nhật bảng hóa đơn
        self.update_invoice_table()

        # Timer for checking new invoices
        self.invoice_check_timer = QTimer(self.MainWindow)
        self.invoice_check_timer.timeout.connect(self.check_new_invoices)
        self.invoice_check_timer.start(10000)  # Check every 10 seconds

    def load_data(self):
        """Tải dữ liệu từ các file JSON"""
        # Đổi directory để đọc file JSON
        os.chdir(self.dataset_path)

        # Đọc dữ liệu từ các file JSON
        self.employees = load_employees()
        self.managers = load_managers()
        self.menu_items = load_menu_items()
        self.shifts = load_shifts()

        # Đọc file invoices.json
        try:
            with open('invoices.json', 'r', encoding='utf-8') as f:
                self.invoices = json.load(f)
        except FileNotFoundError:
            self.invoices = []
            # Tạo file mới nếu chưa tồn tại
            with open('invoices.json', 'w', encoding='utf-8') as f:
                json.dump(self.invoices, f, ensure_ascii=False, indent=4)

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
            # Xóa dữ liệu trong ItemDetailsList khi mới chuyển tab
            self.tableWidget_ItemDetailsList_2.setRowCount(0)
            # Xóa dữ liệu trong các trường nhập liệu
            self.lineEdit_InvoiceID_2.clear()
            self.spinBox_TotalPayment_2.setValue(0)

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
        # Show confirmation dialog first
        msg_box = QMessageBox(self.MainWindow)
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

            self.MainWindow.hide()
            self.login_window = QMainWindow()
            self.login_screen = login_screen_ext()
            self.login_screen.setupUi(self.login_window)
            self.login_screen.showWindow()

    # ======================= DASHBOARD =======================
    def update_dashboard(self):
        """Cập nhật tab Dashboard với dữ liệu thống kê"""
        # Tính toán doanh thu tháng 3/2025
        current_month = "2025-03"
        monthly_revenue = sum(invoice['total'] for invoice in self.invoices if invoice['date'].startswith(current_month))
        
        # Tính toán thống kê khác
        total_employees = len(self.employees)
        total_menu_items = len(self.menu_items)
        total_invoices = len(self.invoices)

        # Tạo định dạng HTML cho các label
        revenue_html = f"""
        <div style='text-align: center;'>
            <span style='font-size: 16pt; font-weight: bold;'>TOTAL REVENUE</span><br>
            <span style='font-size: 12pt; font-weight: bold; color: #FFEB55;'>{monthly_revenue:,} VND</span>
        </div>
        """
        
        employees_html = f"""
        <div style='text-align: center;'>
            <span style='font-size: 16pt; font-weight: bold;'>TOTAL EMPLOYEES</span><br>
            <span style='font-size: 12pt; font-weight: bold; color: #FFEB55;'>{total_employees}</span>
        </div>
        """
        
        menu_items_html = f"""
        <div style='text-align: center;'>
            <span style='font-size: 16pt; font-weight: bold;'>TOTAL MENU ITEMS</span><br>
            <span style='font-size: 12pt; font-weight: bold; color: #FFEB55;'>{total_menu_items}</span>
        </div>
        """
        
        invoices_html = f"""
        <div style='text-align: center;'>
            <span style='font-size: 16pt; font-weight: bold;'>TOTAL INVOICES</span><br>
            <span style='font-size: 12pt; font-weight: bold; color: #FFEB55;'>{total_invoices}</span>
        </div>
        """

        # Hiển thị thông tin tổng quan với định dạng HTML
        self.label_Revenue.setText(revenue_html)
        self.label_TotalEmployees.setText(employees_html)
        self.label_TotalMenuItems.setText(menu_items_html)
        self.label_TotalInvoices.setText(invoices_html)

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
            layout = QtWidgets.QVBoxLayout(self.groupBoxRevenueChart)
            layout.addWidget(revenue_canvas)
        else:
            self.groupBoxRevenueChart.layout().addWidget(revenue_canvas)

        # Màu sắc từ palette
        primary_color = '#2A2F4F'
        secondary_color = '#917FB3'
        accent_color = '#E5BEEC'
        light_color = '#FDE2F3'
        highlight_color = '#FFEB55'

        # Tính toán doanh thu theo buổi cho tháng 3/2025
        current_month = "2025-03"
        morning_revenue = 0
        afternoon_revenue = 0
        evening_revenue = 0

        for invoice in self.invoices:
            if not invoice['date'].startswith(current_month):
                continue
                
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
        shifts = ['Sáng', 'Chiều', 'Tối']
        revenues = [morning_revenue, afternoon_revenue, evening_revenue]

        # Vẽ biểu đồ đường
        ax = revenue_figure.add_subplot(111)
        ax.plot(shifts, revenues, 'o-', linewidth=2, markersize=8, color=secondary_color)
        
        # Thiết lập màu sắc và style
        ax.set_facecolor(light_color)
        revenue_figure.patch.set_facecolor(light_color)
        ax.grid(True, linestyle='--', alpha=0.7, color=primary_color)
        
        # Thiết lập tiêu đề và nhãn
        ax.set_title('Doanh thu theo buổi (Tháng 3/2025)', color=primary_color, fontweight='bold')
        ax.set_ylabel('Doanh thu (VND)', color=primary_color)
        
        # Thiết lập màu cho các thành phần
        ax.spines['bottom'].set_color(primary_color)
        ax.spines['top'].set_color(primary_color)
        ax.spines['left'].set_color(primary_color)
        ax.spines['right'].set_color(primary_color)
        ax.tick_params(axis='x', colors=primary_color)
        ax.tick_params(axis='y', colors=primary_color)

        # Thêm nhãn giá trị
        for i, revenue in enumerate(revenues):
            ax.annotate(f"{revenue:,}", 
                        (i, revenue), 
                        textcoords="offset points",
                        xytext=(0, 10), 
                        ha='center', 
                        color=primary_color,
                        fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", fc=highlight_color, ec=primary_color, alpha=0.8))

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
            layout = QtWidgets.QVBoxLayout(self.groupBoxTop3Chart)
            layout.addWidget(menu_canvas)
        else:
            self.groupBoxTop3Chart.layout().addWidget(menu_canvas)

        # Màu sắc từ palette
        primary_color = '#2A2F4F'
        secondary_color = '#917FB3'
        accent_color = '#E5BEEC'
        light_color = '#FDE2F3'
        highlight_color = '#FFEB55'
        
        # Màu cho pie chart
        pie_colors = [secondary_color, accent_color, highlight_color]

        # Tính toán số lượng bán của từng món
        menu_counter = {}
        
        # Duyệt qua tất cả hóa đơn
        for invoice in self.invoices:
            # Kiểm tra xem có order và items không
            if 'order' in invoice and 'items' in invoice['order']:
                # Duyệt qua từng món ăn trong hóa đơn
                for item in invoice['order']['items']:
                    item_name = item.get('name', '')
                    quantity = item.get('quantity', 0)
                    
                    if item_name:
                        # Cộng dồn số lượng món ăn
                        if item_name in menu_counter:
                            menu_counter[item_name] += quantity
                        else:
                            menu_counter[item_name] = quantity

        # Lấy top 3 món ăn bán chạy nhất
        top_items = sorted(menu_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Nếu không có đủ dữ liệu
        if not top_items:
            ax = menu_figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu', horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes, fontsize=12, color=primary_color)
            menu_canvas.draw()
            return

        # Chuẩn bị dữ liệu cho biểu đồ
        labels = [item[0] for item in top_items]
        sizes = [item[1] for item in top_items]
        
        # Vẽ biểu đồ tròn
        ax = menu_figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%', 
                                         startangle=90, colors=pie_colors,
                                         wedgeprops={'edgecolor': primary_color, 'linewidth': 1})
        
        # Thiết lập màu nền
        menu_figure.patch.set_facecolor(light_color)
        
        # Thiết lập tiêu đề
        ax.set_title('Top 3 món ăn bán chạy nhất', color=primary_color, fontweight='bold')
        
        # Tùy chỉnh màu cho phần trăm
        for autotext in autotexts:
            autotext.set_color(primary_color)
            autotext.set_fontweight('bold')
        
        # Tạo chú thích
        legend = ax.legend(wedges, labels, title="Món ăn", loc="center left", 
                          bbox_to_anchor=(0.85, 0, 0.5, 1))
        legend.get_title().set_color(primary_color)
        legend.get_title().set_fontweight('bold')
        
        # Tùy chỉnh màu cho chú thích
        for text in legend.get_texts():
            text.set_color(primary_color)
        
        # Cập nhật canvas
        menu_canvas.draw()

    # ======================= QUẢN LÝ MENU =======================
    def update_menu_table(self):
        """Cập nhật bảng danh sách món ăn"""
        # Xóa dữ liệu cũ
        self.tableWidget_MenuItemsList_2.setRowCount(0)

        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_MenuItemsList_2.setFont(font)

        # Lọc dữ liệu theo loại món từ comboBox Filter
        selected_category = self.comboBox_ItemFilter_2.currentText()
        filtered_items = self.menu_items

        if selected_category != "All":
            filtered_items = [item for item in self.menu_items
                              if item['category'].lower() == selected_category.lower()]

        # Thêm dữ liệu vào bảng
        self.tableWidget_MenuItemsList_2.setRowCount(len(filtered_items))

        for row, item in enumerate(filtered_items):
            # Mã món
            id_item = QTableWidgetItem(item['id'])
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Vô hiệu hóa chỉnh sửa
            id_item.setFont(font)  # Áp dụng font cho item
            self.tableWidget_MenuItemsList_2.setItem(row, 0, id_item)

            # Tên món
            name_item = QTableWidgetItem(item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Vô hiệu hóa chỉnh sửa
            name_item.setFont(font)  # Áp dụng font cho item
            self.tableWidget_MenuItemsList_2.setItem(row, 1, name_item)

            # Giá
            price_item = QTableWidgetItem(f"{item['price']:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Vô hiệu hóa chỉnh sửa
            price_item.setFont(font)  # Áp dụng font cho item
            self.tableWidget_MenuItemsList_2.setItem(row, 2, price_item)

            # Loại
            category_item = QTableWidgetItem(item['category'])
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Vô hiệu hóa chỉnh sửa
            category_item.setFont(font)  # Áp dụng font cho item
            self.tableWidget_MenuItemsList_2.setItem(row, 3, category_item)

        # Thiết lập font cho header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.tableWidget_MenuItemsList_2.horizontalHeader().setFont(header_font)

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
            QMessageBox.warning(self.MainWindow, "Error", "Please enter all the required information")
            return

        # Kiểm tra mã món đã tồn tại chưa
        for item in self.menu_items:
            if item['id'] == item_id:
                QMessageBox.warning(self.MainWindow, "Error", f"Menu item ID {item_id} already exists")
                return

        # Tạo món ăn mới
        new_item = {
            'id': item_id,
            'name': item_name,
            'price': price,
            'category': category,
            'order_count': 0
        }

        # Thêm vào danh sách
        self.menu_items.append(new_item)

        # Lưu vào file JSON
        self.save_menu_items()

        # Cập nhật bảng
        self.update_menu_table()

        # Xóa dữ liệu nhập
        self.lineEdit_ItemID_2.clear()
        self.lineEdit_ItemName_3.clear()
        self.spinBox_Price_3.clear()

        # Thông báo thành công
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Notification")
        msg_box.setText("Item added successfully")
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

    def edit_menu_item(self):
        """Cho phép chỉnh sửa thông tin món ăn đã chọn"""
        # Kiểm tra có thông tin món ăn nào đang được hiển thị không
        if not self.lineEdit_ItemID_2.text():
            QMessageBox.warning(self.MainWindow, "Error", "Please select the item to edit from the list")
            return

        # Mở khóa các trường nhập liệu để chỉnh sửa (trừ ID vì không nên sửa ID)
        self.lineEdit_ItemName_3.setReadOnly(False)
        self.spinBox_Price_3.setReadOnly(False)
        self.comboBox_Category_2.setEnabled(True)

        # Thông báo cho người dùng
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Notification")
        msg_box.setText("You can edit the food item's information now. Click 'Save Item' to update when done.")
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

    def delete_menu_item(self):
        """Xóa món ăn"""
        # Kiểm tra có hàng nào được chọn không
        selected_rows = self.tableWidget_MenuItemsList_2.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self.MainWindow, "Error", "Please select the item to delete")
            return

        # Lấy mã món của hàng được chọn
        row = selected_rows[0].row()
        item_id = self.tableWidget_MenuItemsList_2.item(row, 0).text()
        item_name = self.tableWidget_MenuItemsList_2.item(row, 1).text()

        # Hiển thị cảnh báo xác nhận
        reply = QMessageBox.question(
            self.MainWindow,
            "Delete confirmation",
            f"Are you sure to delete '{item_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        reply.setStyleSheet("""
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

        if reply == QMessageBox.StandardButton.Yes:
            # Xóa món ăn khỏi danh sách
            self.menu_items = [item for item in self.menu_items if item['id'] != item_id]

            # Lưu vào file JSON
            self.save_menu_items()

            # Cập nhật bảng
            self.update_menu_table()

            # Thông báo thành công
            QMessageBox.information(self.MainWindow, "Notification", "Item deleted successfully")
            QMessageBox.setStyleSheet("""
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

    def save_menu_items(self):
        """Lưu danh sách món ăn vào file JSON"""
        menu_items_path = os.path.join(self.dataset_path, 'menu_items.json')

        with open(menu_items_path, 'w', encoding='utf-8') as f:
            json.dump(self.menu_items, f, ensure_ascii=False, indent=4)

    def save_menu_item_details(self):
        """Lưu thông tin món ăn sau khi chỉnh sửa"""
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
            QMessageBox.warning(self.MainWindow, "Error", "Please enter all the required information")
            return

        # Kiểm tra món ăn đã tồn tại chưa
        item_exists = False
        for item in self.menu_items:
            if item['id'] == item_id:
                item_exists = True
                # Cập nhật thông tin món ăn
                item['name'] = item_name
                item['price'] = price
                item['category'] = category
                break

        # Nếu món ăn chưa tồn tại, thêm mới
        if not item_exists:
            # Tạo món ăn mới
            new_item = {
                'id': item_id,
                'name': item_name,
                'price': price,
                'category': category,
                'order_count': 0
            }
            # Thêm vào danh sách
            self.menu_items.append(new_item)

        # Lưu vào file JSON
        self.save_menu_items()

        # Cập nhật bảng
        self.update_menu_table()

        # Xóa dữ liệu nhập
        self.lineEdit_ItemID_2.setReadOnly(False)  # Bỏ chế độ chỉ đọc
        self.lineEdit_ItemID_2.clear()
        self.lineEdit_ItemName_3.clear()
        self.spinBox_Price_3.clear()

        # Hiển thị QMessageBox xác nhận
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Notification")
        msg_box.setText("Updated successfully!")
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

    # ======================= QUẢN LÝ CA LÀM =======================
    def update_shift_table(self, filtered_shifts=None):
        """Cập nhật bảng danh sách ca làm"""
        # Xóa dữ liệu cũ trong bảng
        self.tableWidget_WorkdayList_2.setRowCount(0)

        # Nếu không có dữ liệu lọc, sử dụng dữ liệu gốc
        if filtered_shifts is None:
            filtered_shifts = self.shifts

        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_WorkdayList_2.setFont(font)

        # Thêm dữ liệu vào bảng
        self.tableWidget_WorkdayList_2.setRowCount(len(filtered_shifts))

        for row, shift in enumerate(filtered_shifts):
            # Mã ca
            id_item = QTableWidgetItem(shift['id'])
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setFont(font)
            self.tableWidget_WorkdayList_2.setItem(row, 0, id_item)

            # Tên ca
            name_item = QTableWidgetItem(shift['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setFont(font)
            self.tableWidget_WorkdayList_2.setItem(row, 1, name_item)

            # Mã NV
            emp_id_item = QTableWidgetItem(shift['employee_id'])
            emp_id_item.setFlags(emp_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            emp_id_item.setFont(font)
            self.tableWidget_WorkdayList_2.setItem(row, 2, emp_id_item)

            # Ngày làm (định dạng từ YYYY-MM-DD sang DD/MM/YYYY)
            date_parts = shift['date'].split('-')
            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
            date_item = QTableWidgetItem(formatted_date)
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            date_item.setFont(font)
            self.tableWidget_WorkdayList_2.setItem(row, 3, date_item)

        # Thiết lập font cho header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.tableWidget_WorkdayList_2.horizontalHeader().setFont(header_font)

        # Điều chỉnh chiều rộng cột
        self.tableWidget_WorkdayList_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_WorkdayList_2.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

    def select_workday(self, item):
        """Hiển thị thông tin ca làm khi chọn một dòng trong bảng"""
        try:
            # Lấy dòng được chọn
            row = item.row()

            # Lấy thông tin từ các cột với kiểm tra null
            shift_id_item = self.tableWidget_WorkdayList_2.item(row, 0)
            shift_name_item = self.tableWidget_WorkdayList_2.item(row, 1)
            employee_id_item = self.tableWidget_WorkdayList_2.item(row, 2)
            date_item = self.tableWidget_WorkdayList_2.item(row, 3)

            # Kiểm tra các item có tồn tại không
            if not all([shift_id_item, shift_name_item, employee_id_item, date_item]):
                print("Some table items are missing")
                return

            # Lấy giá trị text từ các item
            shift_id = shift_id_item.text()
            shift_name = shift_name_item.text()
            employee_id = employee_id_item.text()

            # Hiển thị thông tin vào các trường nhập liệu
            self.lineEdit_ShiftID_2.setText(shift_id)
            self.lineEdit_EmployeeID_3.setText(employee_id)
            self.comboBox_ShiftName_2.setCurrentText(shift_name)

            # Chọn tên ca làm trong comboBox
            index = self.comboBox_ShiftName_2.findText(shift_name)
            if index >= 0:
                self.comboBox_ShiftName_2.setCurrentIndex(index)

            # Xử lý ngày làm việc
            date_str = date_item.text()
            print(f"Date string from table: {date_str}")  # Debug

            # Chuyển đổi chuỗi ngày thành QDate
            try:
                date_parts = date_str.split('/')
                if len(date_parts) == 3:
                    day, month, year = map(int, date_parts)
                    date = QtCore.QDate(year, month, day)
                    print(f"Converted date: {date.toString('dd/MM/yyyy')}")  # Debug
                    self.dateEdit_WorkingDay_2.setDate(date)
                else:
                    print(f"Invalid date format: {date_str}")
            except Exception as date_error:
                print(f"Error parsing date: {date_error}")

            # Lưu thông tin ca làm đã chọn để có thể cập nhật sau này
            for shift in self.shifts:
                if shift['id'] == shift_id:
                    self.selected_shift = shift
                    break

            print(f"Selected workday: ID={shift_id}, Name={shift_name}, Employee={employee_id}, Date={date_str}")

        except Exception as e:
            print(f"Error in select_workday: {e}")

    def filter_shifts(self):
        """Lọc danh sách ca làm theo ngày và Shift Name"""
        # Lấy giá trị ngày từ dateEdit
        selected_date = self.dateEdit_WorkingDayFilter_2.date().toString("yyyy-MM-dd")
        print(f"Selected date for filtering: {selected_date}")  # Debug

        # Lấy giá trị Shift Name từ comboBox
        selected_shift = self.comboBox_ShiftFilter_2.currentText()
        print(f"Selected shift for filtering: {selected_shift}")  # Debug

        # Lọc danh sách ca làm theo ngày trước
        filtered_shifts = [shift for shift in self.shifts if shift['date'] == selected_date]
        print(f"Shifts filtered by date: {len(filtered_shifts)}")  # Debug

        # Sau đó lọc tiếp theo Shift Name nếu không phải "All"
        if selected_shift != "All":
            filtered_shifts = [shift for shift in filtered_shifts if shift['name'] == selected_shift]
            print(f"Shifts filtered by date and shift name: {len(filtered_shifts)}")  # Debug

        # Cập nhật bảng với các ca làm đã lọc
        self.update_shift_table(filtered_shifts)

    def clear_shift_filter(self):
        """Xóa bộ lọc và hiển thị tất cả ca làm"""
        # Đặt lại giá trị mặc định cho dateEdit
        current_date = QtCore.QDate.currentDate()
        self.dateEdit_WorkingDayFilter_2.setDate(current_date)

        # Đặt lại giá trị mặc định cho comboBox Shift
        self.comboBox_ShiftFilter_2.setCurrentIndex(0)  # "All"

        # Cập nhật bảng với tất cả dữ liệu
        self.update_shift_table()  # Pass no arguments to show all shifts

        # Hiển thị thông báo
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Thông báo")
        msg_box.setText("Đã xóa bộ lọc!")
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

    def add_shift(self):
        """Thêm ca làm mới"""
        # Lấy thông tin từ các trường nhập liệu
        shift_id = self.lineEdit_ShiftID_2.text().strip()
        shift_name = self.comboBox_ShiftName_2.currentText()
        employee_id = self.lineEdit_EmployeeID_3.text().strip()
        shift_date = self.dateEdit_WorkingDay_2.date().toString("yyyy-MM-dd")

        # Kiểm tra dữ liệu đầu vào
        if not shift_id or not employee_id:
            QMessageBox.warning(self.MainWindow, "Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # Kiểm tra mã ca đã tồn tại chưa
        for shift in self.shifts:
            if shift['id'] == shift_id:
                QMessageBox.warning(self.MainWindow, "Lỗi", f"Mã ca {shift_id} đã tồn tại")
                return

        # Kiểm tra nhân viên có tồn tại không
        employee_name = ""
        for employee in self.employees:
            if employee['id'] == employee_id:
                employee_name = employee['name']
                break

        if not employee_name:
            QMessageBox.warning(self.MainWindow, "Lỗi", f"Nhân viên với mã {employee_id} không tồn tại")
            return

        # Tạo ca làm mới
        new_shift = {
            'id': shift_id,
            'name': shift_name,
            'employee_id': employee_id,
            'employee_name': employee_name,
            'date': shift_date
        }

        # Thêm vào danh sách
        self.shifts.append(new_shift)

        # Lưu vào file JSON
        self.save_shifts()

        # Cập nhật bảng
        self.update_shift_table()

        # Xóa dữ liệu nhập
        self.lineEdit_ShiftID_2.clear()
        self.lineEdit_EmployeeID_3.clear()

        # Thông báo thành công
        QMessageBox.information(self.MainWindow, "Thông báo", "Thêm ca làm thành công")
        QMessageBox.setStyleSheet("""
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

    def delete_shift(self):
        """Xóa ca làm"""
        # Kiểm tra có hàng nào được chọn không
        selected_rows = self.tableWidget_WorkdayList_2.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self.MainWindow, "Lỗi", "Vui lòng chọn ca làm cần xóa")
            return

        # Lấy mã ca của hàng được chọn
        row = selected_rows[0].row()
        shift_id = self.tableWidget_WorkdayList_2.item(row, 0).text()
        shift_name = self.tableWidget_WorkdayList_2.item(row, 1).text()
        shift_date = self.tableWidget_WorkdayList_2.item(row, 3).text()

        # Hiển thị cảnh báo xác nhận
        reply = QMessageBox.question(
            self.MainWindow,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa ca làm '{shift_name}' ngày {shift_date} không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        reply.setStyleSheet("""
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

        if reply == QMessageBox.StandardButton.Yes:
            # Xóa ca làm khỏi danh sách
            self.shifts = [shift for shift in self.shifts if shift['id'] != shift_id]

            # Lưu vào file JSON
            self.save_shifts()

            # Cập nhật bảng
            self.update_shift_table()

            # Thông báo thành công
            QMessageBox.information(self.MainWindow, "Thông báo", "Xóa ca làm thành công")
            QMessageBox.setStyleSheet("""
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

    def save_shifts(self):
        """Lưu danh sách ca làm vào file JSON"""
        shifts_path = os.path.join(self.dataset_path, 'shifts.json')

        with open(shifts_path, 'w', encoding='utf-8') as f:
            json.dump(self.shifts, f, ensure_ascii=False, indent=4)

    # ======================= QUẢN LÝ HÓA ĐƠN =======================
    def update_invoice_table(self):
        # Xóa dữ liệu cũ trong bảng
        self.tableWidget_InvoiceList_3.setRowCount(0)
        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_InvoiceList_3.setFont(font)
        
        # Kiểm tra file signal để xác định hóa đơn mới nhất
        try:
            signal_file_path = os.path.join(self.dataset_path, 'new_invoice_signal.json')
            if os.path.exists(signal_file_path):
                with open(signal_file_path, 'r', encoding='utf-8') as f:
                    signal_data = json.load(f)
                    self.new_invoice_id = signal_data.get('invoice_id')
        except Exception:
            self.new_invoice_id = None
        
        # Duyệt qua các hóa đơn đã load từ file invoices.json
        for invoice in self.invoices:
            row = self.tableWidget_InvoiceList_3.rowCount()
            self.tableWidget_InvoiceList_3.insertRow(row)
            # Hiển thị 5 cột: Invoice ID, Employee ID, Employee Name, Date, Total Payment

            # Invoice ID
            item_id = QTableWidgetItem(invoice['id'])
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget_InvoiceList_3.setItem(row, 0, item_id)

            # Employee ID
            emp_id = QTableWidgetItem(invoice['employee_id'])
            emp_id.setFlags(emp_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget_InvoiceList_3.setItem(row, 1, emp_id)

            # Date
            date_item = QTableWidgetItem(invoice['date'])
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget_InvoiceList_3.setItem(row, 2, date_item)

            # Total Payment
            total_item = QTableWidgetItem(f"{invoice['total']:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tableWidget_InvoiceList_3.setItem(row, 3, total_item)
            
            # Highlight new invoice with yellow background
            if self.new_invoice_id and invoice['id'] == self.new_invoice_id:
                for col in range(4):
                    item = self.tableWidget_InvoiceList_3.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 235, 85))  # Corrected QColor usage

        # Thiết lập font cho header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.tableWidget_InvoiceList_3.horizontalHeader().setFont(header_font)

        # Điều chỉnh chiều rộng cột
        self.tableWidget_InvoiceList_3.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_InvoiceList_3.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

    def select_invoice(self):
        """Hiển thị chi tiết hóa đơn khi chọn một hóa đơn trong bảng"""
        selected_items = self.tableWidget_InvoiceList_3.selectedItems()
        if not selected_items:
            return
        row = selected_items[0].row()
        invoice_id = self.tableWidget_InvoiceList_3.item(row, 0).text()

        # Tìm hóa đơn tương ứng trong self.invoices
        invoice = next((inv for inv in self.invoices if inv['id'] == invoice_id), None)
        if invoice is None:
            return

        # Hiển thị thông tin hóa đơn trong các trường nhập liệu
        self.lineEdit_InvoiceID_2.setText(invoice['id'])
        self.lineEdit_InvoiceID_2.setReadOnly(True)

        # FIX 2: Hiển thị Employee ID và đặt thành chỉ đọc
        if 'employee_id' in invoice:
            self.lineEdit_EmployeeID_4.setText(invoice['employee_id'])
        else:
            self.lineEdit_EmployeeID_4.setText("")
        self.lineEdit_EmployeeID_4.setReadOnly(True)

        # Chuyển đổi định dạng ngày từ YYYY-MM-DD sang QDate
        date_parts = invoice['date'].split('-')
        if len(date_parts) == 3:
            year, month, day = map(int, date_parts)
            self.dateEdit_PaymentDate_2.setDate(QtCore.QDate(year, month, day))

        # FIX 2: Đặt tất cả các trường thành chỉ đọc
        self.dateEdit_PaymentDate_2.setReadOnly(True)
        self.spinBox_TotalPayment_2.setValue(invoice['total'])
        self.spinBox_TotalPayment_2.setReadOnly(True)

        # Xóa dữ liệu cũ trong bảng chi tiết
        self.tableWidget_ItemDetailsList_2.setRowCount(0)

        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_ItemDetailsList_2.setFont(font)

        # Thêm dòng server/máy với quantity mặc định là 1
        self.tableWidget_ItemDetailsList_2.insertRow(0)

        # Mã server
        server_id_item = QTableWidgetItem("SERVER")
        server_id_item.setFlags(server_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        server_id_item.setFont(font)
        self.tableWidget_ItemDetailsList_2.setItem(0, 0, server_id_item)

        # Tên dịch vụ
        computer_id = invoice['order'].get('computer_id', 'Unknown')
        service_name = QTableWidgetItem(f"Sử dụng máy {computer_id}")
        service_name.setFlags(service_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
        service_name.setFont(font)
        self.tableWidget_ItemDetailsList_2.setItem(0, 1, service_name)

        # Số lượng (mặc định là 1)
        qty_item = QTableWidgetItem("1")
        qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        qty_item.setFont(font)
        self.tableWidget_ItemDetailsList_2.setItem(0, 2, qty_item)

        # Đơn giá (10,000)
        price_item = QTableWidgetItem("10,000")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        price_item.setFont(font)
        self.tableWidget_ItemDetailsList_2.setItem(0, 3, price_item)

        # Thành tiền (time_used * 10,000)
        usage_time = invoice['order'].get('usage_time', 0)
        total_server = usage_time * 10000
        total_item = QTableWidgetItem(f"{total_server:,}")
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        total_item.setFont(font)
        self.tableWidget_ItemDetailsList_2.setItem(0, 4, total_item)

        # Thêm các món ăn từ order
        row_index = 1
        for item in invoice['order']['items']:
            self.tableWidget_ItemDetailsList_2.insertRow(row_index)

            # ID
            item_id = QTableWidgetItem(item.get('item_id', ''))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_id.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row_index, 0, item_id)

            # Tên
            item_name = QTableWidgetItem(item['name'])
            item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_name.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row_index, 1, item_name)

            # Số lượng
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qty_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row_index, 2, qty_item)

            # Đơn giá
            price_item = QTableWidgetItem(f"{item['price']:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row_index, 3, price_item)

            # Thành tiền
            total = item['price'] * item['quantity']
            total_item = QTableWidgetItem(f"{total:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row_index, 4, total_item)

            row_index += 1

        # Thiết lập font cho header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setFont(header_font)

        # Điều chỉnh chiều rộng cột
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(4,
                                                                                   QHeaderView.ResizeMode.ResizeToContents)

    def delete_invoice(self):
        """Xóa hóa đơn"""
        if not self.lineEdit_InvoiceID_2.text():
            QMessageBox.warning(self.MainWindow, "Lỗi", "Vui lòng chọn hóa đơn cần xóa")
            return

        # Hiển thị cảnh báo xác nhận
        reply = QMessageBox.question(
            self.MainWindow,
            "Xác nhận xóa",
            "Bạn có chắc chắn muốn xóa hóa đơn này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        reply.setStyleSheet("""
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

        if reply == QMessageBox.StandardButton.Yes:
            invoice_id = self.lineEdit_InvoiceID_2.text()

            # Xóa hóa đơn khỏi danh sách
            self.invoices = [invoice for invoice in self.invoices if invoice['id'] != invoice_id]

            # Lưu vào file
            self.save_invoices()

            # Cập nhật bảng
            self.update_invoice_table()

            # Xóa thông tin trong các trường
            self.lineEdit_InvoiceID_2.clear()
            self.lineEdit_EmployeeID_4.clear()
            self.spinBox_TotalPayment_2.setValue(0)

            # Xóa dữ liệu trong bảng chi tiết
            self.tableWidget_ItemDetailsList_2.setRowCount(0)

            # Thông báo thành công
            QMessageBox.information(self.MainWindow, "Thông báo", "Đã xóa hóa đơn thành công!")
            QMessageBox.setStyleSheet("""
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

    def add_invoice(self):
        """Thêm hóa đơn mới"""
        # Tạo mã hóa đơn mới
        new_id = f"INV{len(self.invoices) + 1:03d}"

        # Tạo hóa đơn mới
        new_invoice = {
            'id': new_id,
            'employee_id': "",
            'date': QDate.currentDate().toString("yyyy-MM-dd"),
            'time_in': "00:00",
            'time_out': "00:00",
            'order': {
                'customer_name': "",
                'computer_id': "",
                'usage_time': 0,
                'usage_price': 0,
                'items': []
            },
            'total': 0
        }

        # Thêm vào danh sách
        self.invoices.append(new_invoice)

        # Lưu vào file
        self.save_invoices()

        # Cập nhật bảng
        self.update_invoice_table()

        # Hiển thị thông tin hóa đơn mới
        self.lineEdit_InvoiceID_2.setText(new_id)
        self.lineEdit_InvoiceID_2.setReadOnly(True)
        self.lineEdit_EmployeeID_4.setText("")
        self.lineEdit_EmployeeID_4.setReadOnly(True)
        self.dateEdit_PaymentDate_2.setDate(QDate.currentDate())
        self.dateEdit_PaymentDate_2.setReadOnly(True)
        self.spinBox_TotalPayment_2.setValue(0)
        self.spinBox_TotalPayment_2.setReadOnly(True)

        # Xóa dữ liệu trong bảng chi tiết
        self.tableWidget_ItemDetailsList_2.setRowCount(0)

        # Thông báo
        QMessageBox.information(self.MainWindow, "Thông báo", "Đã tạo hóa đơn mới!")
        QMessageBox.setStyleSheet("""
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

    def clear_invoice_filter(self):
        """Xóa bộ lọc và hiển thị tất cả hóa đơn"""
        # Tạm thởi ngắt kết nối tín hiệu dateChanged để tránh gọi filter_invoices
        self.dateEdit_DateFilter_3.dateChanged.disconnect(self.filter_invoices)
        
        # Đặt lại giá trị mặc định cho dateEdit
        current_date = QDate.currentDate()
        self.dateEdit_DateFilter_3.setDate(current_date)
        
        # Kết nối lại tín hiệu dateChanged
        self.dateEdit_DateFilter_3.dateChanged.connect(self.filter_invoices)

        # Đánh dấu là không lọc
        self.is_filtering = False
        self.filter_date = None

        # Cập nhật bảng với tất cả dữ liệu
        self.update_invoice_table()

        # Thông báo khi xóa bộ lọc
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Thông báo")
        msg_box.setText("Đã xóa bộ lọc!")
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

    def save_invoices(self):
        """Lưu danh sách hóa đơn vào file JSON"""
        invoices_path = os.path.join(self.dataset_path, 'invoices.json')

        with open(invoices_path, 'w', encoding='utf-8') as f:
            json.dump(self.invoices, f, ensure_ascii=False, indent=4)

    def select_menu_item(self, item):
        """Hiển thị thông tin của món ăn được chọn trong các ô nhập liệu"""
        # Lấy dòng được chọn
        row = item.row()

        # Lấy thông tin từ các cột
        item_id = self.tableWidget_MenuItemsList_2.item(row, 0).text()
        item_name = self.tableWidget_MenuItemsList_2.item(row, 1).text()

        # Lấy giá (chuyển về dạng số)
        price_text = self.tableWidget_MenuItemsList_2.item(row, 2).text()
        price = int(price_text.replace(',', '').replace('VND', '').strip())

        item_category = self.tableWidget_MenuItemsList_2.item(row, 3).text()

        # Hiển thị thông tin vào các trường nhập liệu
        self.lineEdit_ItemID_2.setText(item_id)
        self.lineEdit_ItemID_2.setReadOnly(True)  # Không cho phép sửa ID khi đã chọn item
        self.lineEdit_ItemName_3.setText(item_name)
        self.lineEdit_ItemName_3.setReadOnly(True)  # Đặt ở chế độ chỉ đọc ban đầu
        self.spinBox_Price_3.setValue(price)
        self.spinBox_Price_3.setReadOnly(True)  # Đặt ở chế độ chỉ đọc ban đầu

        # Vô hiệu hóa comboBox
        self.comboBox_Category_2.setEnabled(False)

        # Tìm và chọn danh mục trong comboBox
        for i in range(self.comboBox_Category_2.count()):
            if self.comboBox_Category_2.itemText(i).lower() == item_category.lower():
                self.comboBox_Category_2.setCurrentIndex(i)
                break

    def add_sample_drink_snack_items(self):
        """Thêm các món mẫu thuộc loại Drink và Snack nếu chưa có"""
        # Kiểm tra nếu đã có món Drink và Snack trong danh sách
        has_drink = any(item['category'] == 'Drink' for item in self.menu_items)
        has_snack = any(item['category'] == 'Snack' for item in self.menu_items)

        if not has_drink and not has_snack:
            # Danh sách món Drink mẫu
            drink_items = [
                {
                    'id': 'DK01',
                    'name': 'Cafe Đen',
                    'price': 20000,
                    'category': 'Drink',
                    'order_count': 0
                },
                {
                    'id': 'DK02',
                    'name': 'Cafe Sữa',
                    'price': 25000,
                    'category': 'Drink',
                    'order_count': 0
                },
                {
                    'id': 'DK03',
                    'name': 'Trà Đào',
                    'price': 30000,
                    'category': 'Drink',
                    'order_count': 0
                },
                {
                    'id': 'DK04',
                    'name': 'Trà Sữa Trân Châu',
                    'price': 35000,
                    'category': 'Drink',
                    'order_count': 0
                },
                {
                    'id': 'DK05',
                    'name': 'Nước Ép Cam',
                    'price': 28000,
                    'category': 'Drink',
                    'order_count': 0
                }
            ]

            # Danh sách món Snack mẫu
            snack_items = [
                {
                    'id': 'SN01',
                    'name': 'Bim Bim Khoai Tây',
                    'price': 15000,
                    'category': 'Snack',
                    'order_count': 0
                },
                {
                    'id': 'SN02',
                    'name': 'Bánh Quy Socola',
                    'price': 20000,
                    'category': 'Snack',
                    'order_count': 0
                },
                {
                    'id': 'SN03',
                    'name': 'Hạt Dẻ Cười',
                    'price': 40000,
                    'category': 'Snack',
                    'order_count': 0
                },
                {
                    'id': 'SN04',
                    'name': 'Hạt Điều Rang',
                    'price': 45000,
                    'category': 'Snack',
                    'order_count': 0
                },
                {
                    'id': 'SN05',
                    'name': 'Kẹo Dẻo',
                    'price': 10000,
                    'category': 'Snack',
                    'order_count': 0
                }
            ]

            # Thêm vào danh sách menu_items
            self.menu_items.extend(drink_items)
            self.menu_items.extend(snack_items)

            # Lưu vào file JSON
            self.save_menu_items()

            # Cập nhật bảng
            self.update_menu_table()

            # Thông báo
            msg_box = QMessageBox(self.MainWindow)
            msg_box.setWindowTitle("Thông báo")
            msg_box.setText("Đã thêm các món mẫu thuộc loại Drink và Snack!")
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

    def on_working_day_changed(self, date):
        """Xử lý khi ngày làm việc thay đổi"""
        if hasattr(self, 'selected_shift'):
            # Cập nhật ngày làm việc mới
            new_date = date.toString("yyyy-MM-dd")
            self.selected_shift['date'] = new_date

            # Cập nhật trong danh sách shifts
            for shift in self.shifts:
                if shift['id'] == self.selected_shift['id']:
                    shift['date'] = new_date
                    break

            # Lưu vào file
            self.save_shifts()

            # Cập nhật bảng
            self.update_shift_table()

            # Hiển thị thông báo
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Đã cập nhật ngày làm việc!")
            msg.setWindowTitle("Thông báo")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2A2F4F;
                    color: #FDE2F3;
                }
                QMessageBox QLabel {
                    color: #FDE2F3;
                    font-size: 12px;
                }
            """)
            msg.exec()

    def filter_invoices(self):
        """Lọc danh sách hóa đơn theo ngày"""
        # Lấy ngày từ dateEdit
        selected_date = self.dateEdit_DateFilter_3.date().toString("yyyy-MM-dd")

        # Xóa dữ liệu cũ trong bảng
        self.tableWidget_InvoiceList_3.setRowCount(0)

        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_InvoiceList_3.setFont(font)

        # Đếm số hóa đơn phù hợp
        filtered_count = 0

        # Duyệt qua các hóa đơn và chỉ hiển thị những hóa đơn có ngày khớp với ngày đã chọn
        for invoice in self.invoices:
            if invoice['date'] == selected_date:
                row = self.tableWidget_InvoiceList_3.rowCount()
                self.tableWidget_InvoiceList_3.insertRow(row)

                # Invoice ID
                item_id = QTableWidgetItem(invoice['id'])
                item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tableWidget_InvoiceList_3.setItem(row, 0, item_id)

                # Employee ID
                emp_id = QTableWidgetItem(invoice['employee_id'])
                emp_id.setFlags(emp_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tableWidget_InvoiceList_3.setItem(row, 1, emp_id)

                # Date
                date_item = QTableWidgetItem(invoice['date'])
                date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tableWidget_InvoiceList_3.setItem(row, 2, date_item)

                # Total Payment
                total_item = QTableWidgetItem(f"{invoice['total']:,}")
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tableWidget_InvoiceList_3.setItem(row, 3, total_item)

                filtered_count += 1

        # Xóa dữ liệu trong bảng chi tiết vì không có hóa đơn nào được chọn
        self.tableWidget_ItemDetailsList_2.setRowCount(0)

        # Lưu trạng thái lọc
        self.is_filtering = True
        self.filter_date = selected_date

        # Thông báo
        msg_box = QMessageBox(self.MainWindow)
        msg_box.setWindowTitle("Thông báo")
        msg_box.setText(f"Đã lọc hóa đơn theo ngày {selected_date}. Tìm thấy {filtered_count} hóa đơn.")
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

    def show_invoice_details(self, item):
        """Hiển thị chi tiết hóa đơn khi chọn một hóa đơn trong bảng"""
        # Lấy hàng được chọn
        row = item.row()
        invoice_id = self.tableWidget_InvoiceList_3.item(row, 0).text()

        # Tìm hóa đơn tương ứng
        selected_invoice = None
        for invoice in self.invoices:
            if invoice['id'] == invoice_id:
                selected_invoice = invoice
                break

        if not selected_invoice:
            return

        # Xóa dữ liệu cũ trong bảng chi tiết
        self.tableWidget_ItemDetailsList_2.setRowCount(0)

        # Thiết lập font size cho bảng
        font = QFont()
        font.setPointSize(12)
        self.tableWidget_ItemDetailsList_2.setFont(font)

        # Thêm thông tin sử dụng máy
        usage_time = selected_invoice['order']['usage_time']
        usage_price = selected_invoice['order']['usage_price']

        if usage_time > 0:  # Chỉ hiển thị nếu có thông tin sử dụng máy
            self.tableWidget_ItemDetailsList_2.insertRow(0)

            # Mã server
            server_id_item = QTableWidgetItem("SERVER")
            server_id_item.setFlags(server_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            server_id_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(0, 0, server_id_item)

            # Tên dịch vụ
            service_name = QTableWidgetItem(f"Sử dụng máy {selected_invoice['order']['computer_id']}")
            service_name.setFlags(service_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
            service_name.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(0, 1, service_name)

            # Số lượng (thời gian sử dụng)
            qty_item = QTableWidgetItem(str(usage_time))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qty_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(0, 2, qty_item)

            # Đơn giá
            unit_price = usage_price / usage_time if usage_time > 0 else 0
            price_item = QTableWidgetItem(f"{unit_price:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(0, 3, price_item)

            # Thành tiền
            total_server = usage_price
            total_item = QTableWidgetItem(f"{total_server:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(0, 4, total_item)

        # Thêm thông tin món ăn
        row = 1 if usage_time > 0 else 0
        for item in selected_invoice['order']['items']:
            self.tableWidget_ItemDetailsList_2.insertRow(row)

            # ID
            item_id = QTableWidgetItem(item.get('item_id', ''))
            item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_id.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row, 0, item_id)

            # Tên
            item_name = QTableWidgetItem(item['name'])
            item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_name.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row, 1, item_name)

            # Số lượng
            qty_item = QTableWidgetItem(str(item['quantity']))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qty_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row, 2, qty_item)

            # Đơn giá
            price_item = QTableWidgetItem(f"{item['price']:,}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            price_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row, 3, price_item)

            # Thành tiền
            total = item['price'] * item['quantity']
            total_item = QTableWidgetItem(f"{total:,}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            total_item.setFont(font)
            self.tableWidget_ItemDetailsList_2.setItem(row, 4, total_item)

            row += 1

        # Thiết lập font cho header
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setFont(header_font)

        # Điều chỉnh chiều rộng cột
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tableWidget_ItemDetailsList_2.horizontalHeader().setSectionResizeMode(4,
                                                                                   QHeaderView.ResizeMode.ResizeToContents)

    def check_new_invoices(self):
        """Kiểm tra hóa đơn mới"""
        # Đọc file invoices.json
        try:
            invoices_json_path = os.path.join(self.dataset_path, 'invoices.json')
            if not os.path.exists(invoices_json_path):
                return
                
            with open(invoices_json_path, 'r', encoding='utf-8') as f:
                new_invoices = json.load(f)
                
            # Check if there are any changes in the invoices
            if len(new_invoices) != len(self.invoices) or any(new_inv["id"] not in [inv["id"] for inv in self.invoices] for new_inv in new_invoices):
                # Update the invoice list
                self.invoices = new_invoices
                
                # Update the invoice table
                self.update_invoice_table()
                
                # Update the dashboard
                self.update_dashboard()
                
                # Check if we're on the invoice tab
                if self.tabWidget.currentIndex() != 3:  # 3 is the index of the invoice tab
                    # Show notification
                    msg_box = QMessageBox(self.MainWindow)
                    msg_box.setWindowTitle("Thông báo")
                    msg_box.setText("Đã có hóa đơn mới!")
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
        except Exception as e:
            print(f"Error checking for new invoices: {e}")