from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.ui_ext_files.employee_screen_ext import employee_screen_ext

app=QApplication([])
myWindow= employee_screen_ext()
myWindow.setupUi(QMainWindow())
myWindow.showWindow()
app.exec()