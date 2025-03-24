from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.ui_ext_files.manager_screen_ext import manager_screen_ext

app=QApplication([])
myWindow= manager_screen_ext()
myWindow.setupUi(QMainWindow())
myWindow.showWindow()
app.exec()