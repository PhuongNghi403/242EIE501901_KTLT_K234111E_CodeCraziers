from PyQt6.QtWidgets import QApplication, QMainWindow

from ui.ui_ext_files.login_screen_ext import login_screen_ext

app=QApplication([])
myWindow= login_screen_ext()
myWindow.setupUi(QMainWindow())
myWindow.showWindow()
app.exec()