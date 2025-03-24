import os
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication, QLineEdit
from dataset.classes_readjson import load_employees, load_managers
from ui.ui_ext_files.employee_screen_ext import employee_screen_ext
from ui.ui_ext_files.manager_screen_ext import manager_screen_ext
from ui.ui_files.login_screen import Ui_MainWindow


class login_screen_ext(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow

        # Connect the login button click event
        self.pushButton_EMLogIn.clicked.connect(self.login)
        self.pushButton_MNLogIn.clicked.connect(self.login)

        # Hook up comboBox change event to switch tabs
        self.comboBox.currentIndexChanged.connect(self.change_tab)

        # Adjust the path to the directory containing the JSON data
        #Get the absolute path to the project root directory
        current_file = os.path.abspath(__file__)
        # Go up 3 levels: ui/ui_ext_files -> ui -> project_root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        dataset_path = os.path.join(project_root, 'dataset')

        # Check if the dataset directory exists
        if os.path.exists(dataset_path):
            os.chdir(dataset_path)
        else:
            print(f"Warning: Dataset directory not found at {dataset_path}")

    def showWindow(self):
        self.MainWindow.show()

    def change_tab(self, index):
        """Switch tabs when user changes selection in comboBox"""
        self.tabWidget.setCurrentIndex(index)

    def login(self):
        """Login handling"""
        # Determine which tab to log in from(Employee or Manager)
        current_tab = self.tabWidget.currentIndex()

        #Get login information from interface based on current tab
        if current_tab == 0:
            employee_id = self.lineEdit_EmployeeID.text().strip()
            password = self.lineEdit_EMPassword.text().strip()
            user_name = self.lineEdit_EmployeeName.text().strip()
        else:
            employee_id = self.lineEdit_ManagerID.text().strip()
            password = self.lineEdit_MNPassword.text().strip()
            user_name = self.lineEdit_ManagerName.text().strip()

        if not employee_id or not password:
            self.show_error("Please enter complete information.")
            return

        #Check ID syntax
        if not self.validate_id_format(employee_id):
            self.show_error("Incorrect syntax Employee ID.\nSuggest: employee ID is in the form EM01, EM02, ... \nManager ID is in the form MN01, MN02, ...")
            return

        #Verify account
        authentication_result = self.authenticate_user(employee_id, password)

        if authentication_result == "employee":
            #Redirect to staff interface
            self.switch_to_employee_screen(employee_id, user_name)
        elif authentication_result == "manager":
            #Redirect to the management interface
            self.switch_to_manager_screen(employee_id, user_name)
        elif authentication_result == "wrong_password":
            self.show_error("Wrong password")
        else:  # authentication_result == "not_found"
            self.show_error("Account does not exist.")

    def validate_id_format(self, employee_id):
        """Check the syntax of the ID"""
        # Employee ID is in the form EM01, EM02, ...
        # The management ID is in the form MN01, MN02, ...
        if (employee_id.startswith("EM") or employee_id.startswith("MN")) and len(employee_id) == 4:
            # Check if the last 2 characters are numbers
            if employee_id[2:].isdigit():
                return True
        return False

    def authenticate_user(self, employee_id, password):
        """Verify login information"""
        # Check Employee ID
        if employee_id.startswith("EM"):
            employees = load_employees()
            for employee in employees:
                if employee["id"] == employee_id:
                    if employee["password"] == password:
                        return "employee"
                    else:
                        return "wrong_password"
            return "not_found"

        #Check manager ID
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
        """Show error message"""
        QMessageBox.critical(self.MainWindow, "Login error", message)

    def switch_to_employee_screen(self, employee_id, user_name):
        """Redirect to staff interface"""
        # Get employee information
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

        # Transmit employee login information
        if current_employee:
            # Use names from input instead of names in database
            current_employee["name"] = user_name if user_name else current_employee["name"]
            self.employee_screen.set_current_employee(current_employee)

        self.employee_screen.showWindow()

    def switch_to_manager_screen(self, manager_id, user_name):
        """Redirect to the management interface"""
        # Get management information
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

        # Transmit login management information
        if current_manager:
            # Use names from input instead of names in database
            current_manager["name"] = user_name if user_name else current_manager["name"]
            self.manager_screen.set_current_manager(current_manager)

        self.manager_screen.showWindow()
