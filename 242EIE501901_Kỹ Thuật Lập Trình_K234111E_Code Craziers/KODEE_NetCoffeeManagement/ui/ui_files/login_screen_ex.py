class login_screen_ex(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Kết nối sự kiện click vào button đăng nhập
        self.pushButton_EMLogIn.clicked.connect(self.login)
        self.pushButton_MNLogIn.clicked.connect(self.login)

        # Kết nối sự kiện comboBox thay đổi để chuyển tab
        self.comboBox.currentIndexChanged.connect(self.change_tab)

        # Điều chỉnh đường dẫn đến thư mục chứa dữ liệu JSON
        # Lấy đường dẫn tuyệt đối đến thư mục gốc của dự án
        current_file = os.path.abspath(__file__)
        # Đi lên 3 cấp: ui/ui_ext_files -> ui -> project_root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        dataset_path = os.path.join(project_root, 'dataset')

        # Kiểm tra xem thư mục dataset có tồn tại không
        if os.path.exists(dataset_path):
            os.chdir(dataset_path)
        else:
            print(f"Warning: Dataset directory not found at {dataset_path}")

    def showWindow(self):
        self.MainWindow.show()

    def change_tab(self, index):
        """Chuyển tab khi người dùng thay đổi lựa chọn trong comboBox"""
        self.tabWidget.setCurrentIndex(index)

    def login(self):
        """Xử lý đăng nhập"""
        # Xác định đăng nhập từ tab nào (Employee hay Manager)
        current_tab = self.tabWidget.currentIndex()

        # Lấy thông tin đăng nhập từ giao diện dựa vào tab hiện tại
        if current_tab == 0:  # Tab Employee
            employee_id = self.lineEdit_EmployeeID.text().strip()
            password = self.lineEdit_EMPassword.text().strip()
            user_name = self.lineEdit_EmployeeName.text().strip()  # Lấy tên từ input
        else:  # Tab Manager
            employee_id = self.lineEdit_ManagerID.text().strip()
            password = self.lineEdit_MNPassword.text().strip()
            user_name = self.lineEdit_ManagerName.text().strip()  # Lấy tên từ input

        # Kiểm tra dữ liệu đầu vào
        if not employee_id or not password:
            self.show_error("Vui lòng nhập đầy đủ thông tin.")
            return

        # Kiểm tra cú pháp ID
        if not self.validate_id_format(employee_id):
            self.show_error(
                "Sai cú pháp Employee ID.\nGợi ý: ID nhân viên có dạng EM01, EM02, ... \nID quản lý có dạng MN01, MN02, ...")
            return

        # Xác thực tài khoản
        authentication_result = self.authenticate_user(employee_id, password)

        if authentication_result == "employee":
            # Chuyển hướng đến giao diện nhân viên
            self.switch_to_employee_screen(employee_id, user_name)
        elif authentication_result == "manager":
            # Chuyển hướng đến giao diện quản lý
            self.switch_to_manager_screen(employee_id, user_name)
        elif authentication_result == "wrong_password":
            self.show_error("Sai mật khẩu.")
        else:  # authentication_result == "not_found"
            self.show_error("Tài khoản không tồn tại.")

    def validate_id_format(self, employee_id):
        """Kiểm tra cú pháp của ID"""
        # ID nhân viên có dạng EM01, EM02, ...
        # ID quản lý có dạng MN01, MN02, ...
        if (employee_id.startswith("EM") or employee_id.startswith("MN")) and len(employee_id) == 4:
            # Kiểm tra 2 ký tự cuối là số
            if employee_id[2:].isdigit():
                return True
        return False

    def authenticate_user(self, employee_id, password):
        """Xác thực thông tin đăng nhập"""
        # Kiểm tra ID nhân viên
        if employee_id.startswith("EM"):
            employees = load_employees()
            for employee in employees:
                if employee["id"] == employee_id:
                    if employee["password"] == password:
                        return "employee"
                    else:
                        return "wrong_password"
            return "not_found"

        # Kiểm tra ID quản lý
        elif employee_id.startswith("MN"):
            managers = load_managers()
            for manager in managers:
                if manager["id"] == employee_id:
                    if manager["password"] == password:
                        return "manager"
                    else:
                        return "wrong_password"
            return "not_found"

        return "not_found"

    def show_error(self, message):
        """Hiển thị thông báo lỗi"""
        QMessageBox.critical(self.MainWindow, "Lỗi đăng nhập", message)

    def switch_to_employee_screen(self, employee_id, user_name):
        """Chuyển hướng đến giao diện nhân viên"""
        # Lấy thông tin nhân viên
        employees = load_employees()
        current_employee = None
        for employee in employees:
            if employee["id"] == employee_id:
                current_employee = employee
                break

        self.MainWindow.hide()
        self.employee_window = QMainWindow()
        self.employee_screen = employee_screen_ext()
        self.employee_screen.setupUi(self.employee_window)

        # Truyền thông tin nhân viên đăng nhập
        if current_employee:
            # Sử dụng tên từ input thay vì tên trong cơ sở dữ liệu
            current_employee["name"] = user_name if user_name else current_employee["name"]
            self.employee_screen.set_current_employee(current_employee)

        self.employee_screen.showWindow()

    def switch_to_manager_screen(self, manager_id, user_name):
        """Chuyển hướng đến giao diện quản lý"""
        # Lấy thông tin quản lý
        managers = load_managers()
        current_manager = None
        for manager in managers:
            if manager["id"] == manager_id:
                current_manager = manager
                break

        self.MainWindow.hide()
        self.manager_window = QMainWindow()
        self.manager_screen = manager_screen_ext()
        self.manager_screen.setupUi(self.manager_window)

        # Truyền thông tin quản lý đăng nhập
        if current_manager:
            # Sử dụng tên từ input thay vì tên trong cơ sở dữ liệu
            current_manager["name"] = user_name if user_name else current_manager["name"]
            self.manager_screen.set_current_manager(current_manager)

        self.manager_screen.showWindow()
