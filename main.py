from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton, QMessageBox, \
    QFileDialog, QInputDialog
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTime, QThread
from UI.design import Ui_MainWindow
from time import sleep
import serial  # библиотека дя работы с последовательными портами
from serial.tools.list_ports import comports  # функция, возвращающая список доступных портов
import sys
import csv
import sqlite3

# TODO:
#  1. добавить возможность задавать названия столбцов


# словарь для преобразования значений выпадающих списков
CHAR_REF = {'\\r\\n': '\r\n', '\\n': '\n', '\\r': '\r', '\\t': '\t'}


# преобразует матрицу для sql запроса
def prepare_data(data):
    type_ref = [int if all([row[n] or not row[n] is int for n in range(len(data[-1]))]) else str for
                row in data]
    rows = ', '.join(
            [str(tuple([str(val) if type_ref[n] == str else val for n, val in enumerate(row)]))
             for row in data])
    return rows


# Параллельный поток приёма значений через последовательный порт
# Нужен вследствие того, что приём значений - блокирующая операция
class SerialUpdateThread(QThread):
    def __init__(self, main, serial_port, data, delimiter):
        self.main = main  # ссылка на основное окно для доступа к основным виджетам
        self.ser = serial_port
        self.delim = delimiter
        self.data = data
        self.timer = QTime()

        super().__init__()

    def run(self):
        while self.main.connection:
            # обработка потери соединения и истечения времени приёма
            try:
                # если есть данные на входе, считываем их и дополняем таблицу
                if self.ser.in_waiting:
                    line = self.ser.readline().strip().split(self.delim.encode())
                    line.insert(0, self.timer.currentTime().toString("H:mm:ss.z") *
                                self.main.time_chk.isChecked())
                    self.main.model.beginResetModel()
                    for i in range(len(line)):
                        if type(line[i]) != str:
                            line[i] = line[i].decode()
                            if line[i].isdigit():
                                line[i] = int(line[i])
                    self.data.append(line)
                    self.main.model.endResetModel()
                    if self.main.scroll_chk.isChecked():
                        self.main.out_field.scrollToBottom()
                        # self.main.model.dataChanged.emmit(self.main.model.createIndex(0, 0))
            # если время приёма вышло, просто пытаемся принять ещё раз
            except serial.serialutil.SerialTimeoutException:
                sleep(0.01)

            # если теряется соединение, выводим сообщение об ошибке и закрываем порт
            except OSError:
                self.main.error_msg.setText('Device disconnected! Check wiring')
                self.main.error_tab.exec()
                self.main.refresh_ports_list()
                self.finished.emit()
                break


# для вывода значений применяется model/view подход
class TableModel(QAbstractTableModel):  # класс модели для отображения значений в TableView
    def __init__(self, main, data):
        self.main = main
        super().__init__()
        self.data_table = data

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.data_table)

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        if self.data_table:
            if self.main.time_chk.isChecked():
                return len(self.data_table[0])
            else:
                return len(self.data_table[0]) - 1
        else:
            return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if self.main.time_chk.isChecked():
                return section
            else:
                return section + 1

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if len(self.data_table):
                row = index.row() + (not self.main.time_chk.isChecked())
                col = index.column() + (not self.main.time_chk.isChecked())
                if row < len(self.data_table) and col < len(self.data_table[row]):
                    return self.data_table[row][col]
        return None


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data = []

        # окно для вывода сообщения об ошибке, QMessageBox плохо работает с параллельными потоками
        self.error_tab = QDialog(self)
        self.error_tab.setWindowTitle('Error')
        self.error_tab.resize(400, 100)
        self.error_msg = QLabel('', self.error_tab)
        self.ok_btn = QPushButton('Ok', self.error_tab)
        self.ok_btn.move(180, 70)
        self.ok_btn.setDefault(1)
        self.ok_btn.clicked.connect(self.error_tab.close)
        self.error_msg.move(45, 10)
        self.error_msg.resize(310, 60)
        self.error_msg.setAlignment(Qt.AlignCenter)

        self.exit_msg = QMessageBox()  # окно предупреждения о выходе
        self.exit_msg.setText('Выйти из приложения?')
        self.exit_msg.setInformativeText('Все несохранённые данные будут потеряны, продолжить?')
        self.exit_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.exit_msg.setDefaultButton(QMessageBox.No)

        for baudrate in serial.Serial.BAUDRATES:  # заполнение возможных скоростей соединеня
            self.baudrate_box.addItem(str(baudrate) + ' бод')
        self.baudrate_box.setCurrentIndex(12)

        # подключение кнопок
        self.refresh_btn.clicked.connect(self.refresh_ports_list)
        self.refresh_ports_list()

        self.connection = False
        self.connect_btn.clicked.connect(self.start_connection)

        self.send_btn.clicked.connect(self.send)
        self.clear_btn.clicked.connect(self.clear_out)

        self.model = TableModel(self, self.data)
        self.out_field.setModel(self.model)

        self.dsv_export_btn.clicked.connect(self.dsv_export)

        self.sql_connect_btn.clicked.connect(self.connect_sql_bd)
        self.sql_new_table_btn.clicked.connect(self.add_sql_table)
        self.sql_overwrite_btn.clicked.connect(self.overwrite_sql_table)
        self.sql_add_btn.clicked.connect(self.append_to_sql_table)

        self.show()

    # функция запуска подключения через последовательный порт
    def start_connection(self):
        baudrate = int(self.baudrate_box.currentText().split()[0])
        port = self.port_box.currentText()
        delimiter = self.input_delim_box.currentText()
        delimiter = CHAR_REF.get(delimiter, delimiter)
        # обработка открытия порта
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

            # запускаем поток приёма данных
            self.update_thread = SerialUpdateThread(self, self.ser, self.data, delimiter)
            self.update_thread.finished.connect(self.stop_connection)
            self.update_thread.start()

        # если не удалось подключиться, выводим сообщение об ошибке
        except serial.serialutil.SerialException:
            self.refresh_ports_list()
            self.error_msg.setText('Connection failed! Check connection settings')
            self.error_tab.exec()

        self.update()

    # функция остановки соединения
    def stop_connection(self):
        self.connection = False
        while self.update_thread.isRunning():  # ждём остановки потока приёма данных
            sleep(0.01)
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

    # функция отправки данных через последовательный порт
    def send(self):
        if self.connection:
            self.ser.write(self.input_line.text().encode('utf8'))
            end = self.end_box.currentText()
            self.ser.write(CHAR_REF.get(end, end).encode('utf8'))
            self.input_line.clear()
        self.update()

    # функция обновления списка доступных портов
    def refresh_ports_list(self):
        self.port_box.clear()
        for port, _, _ in comports():
            self.port_box.addItem(port)

    # функция очистки окна вывода
    def clear_out(self):
        self.model.beginResetModel()
        self.data.clear()
        self.model.endResetModel()

    # вывод предупреждения при выходе
    def closeEvent(self, close_event):
        if self.exit_msg.exec() == QMessageBox.Yes:
            if self.connection:
                self.stop_connection()
            close_event.accept()
        else:
            close_event.ignore()

    # экспорт в формат таблицы с разделителем
    def dsv_export(self):
        name, *_ = QFileDialog.getSaveFileName(self, 'Экспортировать в dsv', '', 'CSV(*.csv)')
        if name:
            with open(name, mode='w') as out:
                delimiter = self.dsv_delim_box.currentText()
                delimiter = CHAR_REF.get(delimiter, delimiter)
                writer = csv.writer(out, delimiter=delimiter,
                                    quotechar=self.dsv_quote_box.currentText())
                writer.writerows(self.data)

    # подключение к sql базе данных
    def connect_sql_bd(self):
        path, *_ = QFileDialog.getOpenFileName(self, 'Выбрать базу данных', '', "БД(*.db)")
        if path:
            self.con = sqlite3.connect(path)
            self.cur = self.con.cursor()

            # получаем список таблиц
            tables = self.cur.execute("select * from sqlite_master where type = 'table'").fetchall()
            for table_name in [table[2] for table in tables]:
                self.sql_table_box.addItem(table_name)

            self.sql_table_box.setEnabled(True)
            self.sql_add_btn.setEnabled(True)
            self.sql_new_table_btn.setEnabled(True)
            self.sql_overwrite_btn.setEnabled(True)

            self.sql_connect_btn.disconnect()
            self.sql_connect_btn.setText('Отключить базу данных')
            self.sql_connect_btn.clicked.connect(self.disconnect_sql_bd)

    # отключение от sql базы данных с сохранением изменнений
    def disconnect_sql_bd(self):
        self.con.commit()
        self.cur.close()
        self.con.close()

        self.sql_table_box.setEnabled(False)
        self.sql_add_btn.setEnabled(False)
        self.sql_new_table_btn.setEnabled(False)
        self.sql_overwrite_btn.setEnabled(False)
        self.sql_table_box.clear()

        self.sql_connect_btn.disconnect()
        self.sql_connect_btn.setText('Подключить базу данных...')
        self.sql_connect_btn.clicked.connect(self.connect_sql_bd)

    # добавление таблицы в sql базу данных
    def add_sql_table(self):
        if self.data:
            table_name, ok = QInputDialog.getText(self, 'Новая таблица', 'Введите название таблицы')
            if ok:
                table_name = '[' + table_name + ']'
                columns = []
                for n in range(len(self.data[0])):
                    data_type = 'int' if all(
                            [line[n] is int or not line[n] for line in self.data if line[n]]) else 'string'
                    col_name = '[' + str(n) + ']'  # экранироание на случай неправильных названий
                    columns.append(col_name + ' ' + data_type)
                try:
                    self.cur.execute(f'''CREATE TABLE {table_name} ({', '.join(columns)});''')
                    self.sql_table_box.addItem(table_name.strip('[]'))

                # возможность ввода некорректного названия остаётся
                except sqlite3.OperationalError:
                    self.error_msg.setText('''Не удалось создать таблицу. 
    Проверьте корректность названия''')
                    self.error_tab.exec()
        else:  # если нет данных, то нельзя определить форму таблицы
            self.error_msg.setText('Нет данных для создания таблицы')
            self.error_tab.exec()

    # добавление данных в конец таблицы
    def append_to_sql_table(self):
        table_name = '[' + self.sql_table_box.currentText() + ']'
        rows = prepare_data(self.data)  # форматируем данные для sql запроса
        try:
            self.cur.execute(f'''INSERT INTO {table_name} VALUES {rows}''')
            self.con.commit()
            del rows

        # размерность или типы данных несовместимы с имеющейся таблицей
        except sqlite3.OperationalError:
            self.error_msg.setText('''Ошибка записи. Формат таблицы не 
       соответствует формату данных''')
            self.error_tab.exec()

    # перезапись таблицы
    def overwrite_sql_table(self):
        table_name = '[' + self.sql_table_box.currentText() + ']'
        self.cur.execute(f'DELETE from {table_name}')  # очищаем исходную таблицу
        rows = prepare_data(self.data)  # форматируем данные для sql запроса
        try:
            self.cur.execute(f'''INSERT INTO {table_name} VALUES {rows}''')
            self.con.commit()
            del rows

        # размерность или типы данных несовместимы с имеющейся таблицей
        except sqlite3.OperationalError:
            self.error_msg.setText('''Ошибка записи. Формат таблицы не 
       соответствует формату данных''')
            self.error_tab.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
