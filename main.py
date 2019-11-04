from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer, QTime, QThread
from design import Ui_MainWindow
from time import sleep
import serial
from serial.tools.list_ports import comports
import sys

CHAR_REF = {'\\n\\r': '\n\r', '\\n': '\n', '\\r': '\r', '\\t': '\t'}


class SerialUpdateThread(QThread):
    def __init__(self, main, serial_port, data, delimiter):
        self.main = main
        self.ser = serial_port
        self.delim = delimiter
        self.data = data
        self.timer = QTime()

        super().__init__()

    def run(self):
        while self.main.connection:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().strip().split(self.delim.encode())
                    if self.main.time_chk.isChecked():
                        line.insert(0, self.timer.currentTime().toString("H:mm:ss.z"))
                    if line:
                        self.main.model.beginResetModel()
                        for i in range(len(line)):
                            if line[i].isdigit():
                                line[i] = int(line[i])
                            elif type(line[i]) != str and line[i].isalpha():
                                line[i] = line[i].decode()
                        self.data.append(line)
                        self.main.model.endResetModel()
                        if self.main.scroll_chk.isChecked():
                            self.main.out_field.scrollToBottom()
                        # self.main.model.dataChanged.emmit(self.main.model.createIndex(0, 0))
            except serial.serialutil.SerialTimeoutException:
                pass

            except OSError:
                self.main.stop_connection()
                self.main.error_msg.setText('Device disconnected! Check wiring')
                self.main.error_tab.exec()
                self.main.refresh_ports_list()


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        if len(self.data):
            return len(self.data[-1])
        else:
            return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return section

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if index.row() < len(self.data) and index.column() < len(self.data[index.row()]):
            return self.data[index.row()][index.column()]
        else:
            return None


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data = []

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

        self.send_btn.clicked.connect(self.send)
        self.clear_btn.clicked.connect(self.clear_out)

        self.model = TableModel(self.data)
        self.out_field.setModel(self.model)

        self.show()

    def start_connection(self):
        baudrate = int(self.baudrate_box.currentText().split()[0])
        port = self.port_box.currentText()
        delimiter = self.input_delim_box.currentText()
        delimiter = CHAR_REF.get(delimiter, delimiter)
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.5)
            self.baudrate_box.setEnabled(False)
            self.port_box.setEnabled(False)
            self.input_delim_box.setEnabled(False)
            self.refresh_btn.setEnabled(False)
            self.send_btn.setEnabled(True)

            self.connection = True
            self.connect_btn.clicked.disconnect()
            self.connect_btn.clicked.connect(self.stop_connection)
            self.connect_btn.setText('Отключиться')
            self.update_thread = SerialUpdateThread(self, self.ser, self.data, delimiter)
            self.update_thread.start()

        except serial.serialutil.SerialException:
            self.refresh_ports_list()
            self.error_msg.setText('Connection failed! Check connection settings')
            self.error_tab.exec()

        self.update()

    def stop_connection(self):
        self.connection = False
        sleep(0.6)
        self.ser.close()
        self.baudrate_box.setEnabled(True)
        self.port_box.setEnabled(True)
        self.input_delim_box.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.send_btn.setEnabled(False)
        self.connect_btn.clicked.disconnect()
        self.connect_btn.clicked.connect(self.start_connection)
        self.connect_btn.setText('Подключиться')
        self.update()

    def send(self):
        if self.connection:
            for val in self.input_line.text().split():
                if val.isdigit():
                    val = int.to_bytes(int(val), 1, 'big')
                else:
                    val = val.encode('utf8')
                self.ser.write(val)
                self.ser.write(' '.encode('utf8'))
            end = self.end_box.currentText()
            self.ser.write(CHAR_REF.get(end, end).encode('utf8'))
            self.input_line.clear()

    def refresh_ports_list(self):
        self.port_box.clear()
        for port, _, _ in comports():
            self.port_box.addItem(port)

    def clear_out(self):
        self.model.beginResetModel()
        self.data.clear()
        self.model.endResetModel()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
