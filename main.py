from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer, QTime, QThread
from design import Ui_MainWindow
import serial
from serial.tools.list_ports import comports
import sys

CHAR_REF = {'\\n\\r': '\n\r', '\\n': '\n', '\\r': '\r', '\\t': '\t'}


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        if len(self.data):
            return len(self.data[0])
        else:
            return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return 1

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            print(0)
            return None
        print(2)
        return self.data[index.row()][index.column()]


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
        self.scroll_chk.clicked.connect(self.switch_scroll)
        self.clear_btn.clicked.connect(self.clear_out)

        self.update_timer = QTimer()
        self.update_timer.setInterval(100)
        self.update_timer.start()

        self.model = TableModel(self.data)
        self.out_field.setModel(self.model)

        self.timer = QTime()
        self.timer.start()

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
            self.send_btn.setEnabled(True)
            self.connection = True
            self.connect_btn.clicked.disconnect()

            self.connect_btn.clicked.connect(self.stop_connection)
            self.connect_btn.setText('Отключиться')
            print(self.data)
            self.update_thread = SerialUpdateThread(self, self.ser, self.data, delimiter)
            self.update_thread.exec()

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
        self.connect_btn.setText('Подключиться')
        self.update()
        print(self.data)


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
