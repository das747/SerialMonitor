from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton
from PyQt5.QtCore import Qt
from design import Ui_MainWindow
import serial
from serial.tools.list_ports import comports
import sys


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.error_tab = QDialog(self)
        self.error_tab.setWindowTitle('Error')
        self.error_tab.resize(400, 65)
        self.error_msg = QLabel('', self.error_tab)
        self.ok_btn = QPushButton('Ok', self.error_tab)
        self.ok_btn.move(180, 35)
        self.ok_btn.setDefault(1)
        self.ok_btn.clicked.connect(self.error_tab.close)
        self.error_msg.move(45, 10)
        self.error_msg.setAlignment(Qt.AlignCenter)

        for baudrate in serial.Serial.BAUDRATES:
            self.baudrate_box.addItem(str(baudrate) + ' бод')
        self.baudrate_box.setCurrentIndex(12)

        self.refresh_btn.clicked.connect(self.refresh_ports_list)
        self.refresh_ports_list()

        self.connection = False
        self.connect_btn.clicked.connect(self.start_connection)

        self.scroll_chk.clicked.connect(self.switch_scroll)
        self.show()

    def start_connection(self):
        baudrate = int(self.baudrate_box.currentText().split()[0])
        port = self.port_box.currentText()
        delimiter = self.input_delim_box.currentText()
        try:
            self.ser = serial.Serial(port, baudrate)
            self.baudrate_box.setEnabled(False)
            self.port_box.setEnabled(False)
            self.input_delim_box.setEnabled(False)
            self.send_btn.setEnabled(True)
            self.connection = True
            self.connect_btn.clicked.disconnect()
            self.connect_btn.clicked.connect(self.stop_connection)

        except serial.serialutil.SerialException:
            self.error_msg.setText('Connection failed! Check connection settings')
            self.error_tab.exec()
        self.update()

    def stop_connection(self):
        self.baudrate_box.setEnabled(True)
        self.port_box.setEnabled(True)
        self.input_delim_box.setEnabled(True)
        self.send_btn.setEnabled(False)
        self.connection = False
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.start_connection)
        self.update()

    def update_data(self):
        if self.connection:  # and self.ser.in_waiting:
            delimiter = self.input_delim_box.currentText()
            delimiter = CHAR_REF.get(delimiter, delimiter)
            line = self.ser.readline().strip().split()
            if self.time_chk.isChecked():
                line.insert(0, self.timer.toString())
            if line:
                self.data.append(list(map(lambda v: int(v) if v.isdigit() else v, line)))
                self.model.dataChanged.emit(self.model.createIndex(0, 1),
                                            self.model.createIndex(0, 1))
                print(1)
    def refresh_ports_list(self):
        self.port_box.clear()
        for port, _, _ in comports():
            self.port_box.addItem(port)

    def switch_scroll(self):
        self.out_field.setAutoScroll(self.scroll_chk.isChecked())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
