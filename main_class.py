from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from time import *
from window import Ui_MainWindow
from parser_class import *
import sys

x_offset = 40
y_top_offset = 100
y_bottom_offset = 100
stat_row_offset = 20

regex = re.compile(r"[aA0-zZ9]+|[аА-яЯ9]+|[ё]|[Ё]|[і]|[І]|[ї]|[Ї]|[є]|[Є]|\.|[ ]|[\,]|[\?]|[\:]|[\;]|[\-]|[\+]|[\=]|[\(]|[\)]|[\*]|[\&]|[\^]|[\%]|[\$]|[\#]|[\@]|[\!]|[\~]|[\`]|[\']")

statistics = {
    'time': 0,
    'text-size': 0,
    'symbols-typed': 0,
    'symbols-failed': 0,
    'accuracy': 0,
}

# frame = 71, 66, 66
# bg = 46, 42, 42
# 

class main_class(QtWidgets.QMainWindow):
    def __init__(self, language = 'en', text_length = 200):
        super(main_class, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parser = parser_class(language)
        self.text = None

        self.ui.check_lowercase.stateChanged.connect(self.lower_only)
        self.ui.min_line.editingFinished.connect(self.min_edited)
        self.ui.new_button.clicked.connect(self.new_round)
        self.ui.leave_button.clicked.connect(self.leave_round)
        self.ui.leave_button.setEnabled(False)

        self.LOWERCASE_ONLY = False
        self.isGame = False
        self.x_smooth = 0
        self.pushes = 0
        self.push_forge = 0
        
        if text_length >= 200:
            self.min = text_length
        else:
            self.min = 200
        
        self.everySecondTimer = self.startTimer(1000)
        self.everyRedrawTimer = self.startTimer(250)
        self.animationTimer = self.startTimer(33)
        self.reset_counters()

        self.show()

    def set_text(self):
        self.parser.set_language(self.ui.lang_list.currentText()[0:2])
        self.text = self.parser.text(self.min)

        if not self.text:
            self.set_text()

        self.text = str_from_list(regex.findall(self.text))
        
        self.text = self.text.replace('  ', ' ')
        self.text = self.text.strip()
        
        if self.LOWERCASE_ONLY:
            self.text = self.text.lower()

        statistics['text-size'] = len(self.text)

    def update(self):
        self.ui.timer.setText(str(self.timer) + ' s')
        if self.timer != 0:
            self.spm = round(self.symbols_typed / (self.timer / 60), 1)
        self.ui.spm.setText(str(self.spm) + ' s/m')
        self.ui.acc.setText(str(self.acc) + ' %')
        
        super().update()

    def timerEvent(self, event):
        if self.isGame:
            if self.everySecondTimer == event.timerId():
                self.timer += 1

            if self.everyRedrawTimer == event.timerId():
                self.update()

            if self.animationTimer == event.timerId():
                if self.x_smooth > 0:
                    if self.x_smooth < 0.05:
                        self.x_smooth = 0
                        self.update()
                    else:
                        self.x_smooth -= self.x_smooth / 16
                        self.update()       
        super().timerEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0, 0))
        painter.setBrush(QColor(46, 42, 42))
        painter.drawRect(self.rect())

        if self.isGame:
            painter.setBrush(QColor(255, 163, 163))
            self.draw_current_symbol(painter)
            self.draw_text(painter)
        else:
            self.draw_statistics(painter)

    def new_round(self):
        self.set_text()
        self.isGame = True
        self.reset_counters()
        self.ui.leave_button.setEnabled(self.isGame)
        self.ui.new_button.setEnabled(not self.isGame)
        self.ui.leave_button.clearFocus()
        self.ui.min_line.clearFocus()

    def leave_round(self):
        self.isGame = False
        self.ui.leave_button.setEnabled(self.isGame)
        self.ui.new_button.setEnabled(not self.isGame)
        if self.timer == 0:
            self.timer = 1
        self.fill_statistics()
        self.update()

    def draw_current_symbol(self, qp):
        qp.drawRect(QRect(x_offset - 5 + (self.x_smooth // 1.25), y_top_offset - (10 + self.x_smooth // 8), 2, 40 + self.x_smooth // 4))
        qp.setPen(QColor(255, 163, 163))
        qp.drawText(QRect(x_offset + self.x_smooth - 2, y_top_offset - 1, 1000, 500), Qt.AlignLeft, self.text[0])

    def draw_text(self, qp):
        qp.setPen(QColor(207, 200, 200))
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset, 1000, 500), Qt.AlignLeft, self.text[1:90])

    def draw_statistics(self, qp):
        qp.setPen(QColor(207, 200, 200))
        qp.drawText(QRect(x_offset - 20 + self.x_smooth, y_top_offset - 20, 1000, 500), Qt.AlignLeft, 'Statistics:')
        
        qp.setPen(QColor(191, 155, 155))
        if statistics['time'] > 60:
            qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 0, 1000, 500), Qt.AlignLeft, 'time: ' + str(statistics['time'] // 60) + ' minuts ' + str(statistics['time'] % 60) + ' seconds')
        else:
            qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 0, 1000, 500), Qt.AlignLeft, 'time: ' + str(statistics['time']) + ' seconds')

        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 1, 1000, 500), Qt.AlignLeft, 'accuracy: ' + str(statistics['accuracy']) + ' %')
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 2, 1000, 500), Qt.AlignLeft, 'text size: ' + str(statistics['text-size']) + ' symbols')
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 3, 1000, 500), Qt.AlignLeft, 'symbols writed: ' + str(statistics['symbols-typed']) + ' symbols')
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 4, 1000, 500), Qt.AlignLeft, 'symbols failed: ' + str(statistics['symbols-failed']) + ' symbols')
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 5, 1000, 500), Qt.AlignLeft, 'speed (sec): ' + str(round(self.symbols_typed / self.timer, 1)) + ' symbols/second')
        qp.drawText(QRect(x_offset + 10 + self.x_smooth, y_top_offset + stat_row_offset * 6, 1000, 500), Qt.AlignLeft, 'speed (min): ' + str(round(self.symbols_typed / (self.timer / 60), 1)) + ' symbols/minut')

    def keyPressEvent(self, e):
        if self.isGame:
            key = e.text()
            if str_from_list(regex.findall(key)):
                self.symbols_typed += 1

                if key == self.text[0]:
                    self.text = self.text[1:]
                    self.x_smooth += 10
                    if len(self.text) == 0:
                        self.leave_round()
                else:
                    self.fails += 1
                self.acc = round(100 - (self.fails * 100) / self.symbols_typed, 2)
                self.update()

    def reset_counters(self):
        self.timer = -1
        self.spm = 0
        self.acc = 0
        self.fails = 0
        self.symbols_typed = 0

    def fill_statistics(self):
        statistics['symbols-typed'] = self.symbols_typed
        statistics['symbols-failed'] = self.fails
        statistics['accuracy'] = self.acc
        statistics['time'] = self.timer

    def lower_only(self, state):
        if state:
            self.LOWERCASE_ONLY = True
        else:
            self.LOWERCASE_ONLY = False

    def min_edited(self):
        if self.ui.min_line.text().isdigit():
            if int(self.ui.min_line.text()) > 1000:
                self.ui.min_line.setText(str(1000))
            elif int(self.ui.min_line.text()) < 200:
                self.ui.min_line.setText(str(200))
        else:
            self.ui.min_line.setText(str(1000))
        self.min = int(self.ui.min_line.text())

def str_from_list(listr):
    temp = ""
    for item in listr:
        temp += item
    return temp