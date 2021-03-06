# -*- coding: utf-8 -*-

import sys
from datetime import date, timedelta
from pathlib import Path
import images.outputResources
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui
from pyqtgraph import PlotWidget
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from os import path

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

displayingfile = ""  # File on which output is being calcuated
displayingHeadlines = ["A", "B", "C", "D"]  # default headlines
displayingScores = [0.0, 0.0, 0.0, 0.0]  # Default scores
lineNumber = 0  # Keeping track of headlines in file , to display 4 headlines at a time
outputDate = date.today()  # Default date to show output on is today. Changes when selected from calender
calculatingAccuracy = False  # Flag to indicate if we are in calculate Accuracy mode
wrongScoreCounter = 0  # To calculate Accuracy
headlinesDisplayedCounter = 0
allHeadlinesShown = False


def drawWordCloud():
    # Read the whole text.
    text = open(displayingfile).read()
    # Generate a word cloud image
    circle_mask = np.array(Image.open("./images/mask.png"))
    wordcloud = WordCloud(max_words=300, mask=circle_mask).generate(text)  # , width=560, height=321

    wordcloud.to_file("./data/wc.png")
    # wordcloud.to_file("../data/wc.png") #testing


def makeGraph(graphView):
    pg.setConfigOptions(antialias=True)

    y_axis_pos = []
    x_axis_pos = []
    y_axis_neg = []
    x_axis_neg = []
    y_axis_zero = []
    x_axis_zero = []
    line_counter = 0
    with open(displayingfile, "r") as f:
        for line in f:
            if line.startswith(">>"):
                num = float(line[3:].rstrip("\n"))
                line_counter += 1
                if num > 0:
                    y_axis_pos.append(num)
                    x_axis_pos.append(line_counter)
                if num < 0:
                    y_axis_neg.append(num)
                    x_axis_neg.append(line_counter)
                if num == 0:
                    y_axis_zero.append(num)
                    x_axis_zero.append(line_counter)

    graphView.plot(x_axis_pos, y_axis_pos, pen=(200, 200, 200), symbolBrush=(0, 255, 0), symbolPen='r')
    graphView.plot(x_axis_neg, y_axis_neg, pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='b')
    graphView.plot(x_axis_zero, y_axis_zero, pen=(0, 0, 0), symbolBrush=(255, 255, 255), symbolPen='k')


def headline_display_color(score):
    rgw = ["#ff7f7f", "#28ff41", "#ffffff"]
    if score > 0:
        return rgw[1]  # Green
    if score < 0:
        return rgw[0]  # Red

    return rgw[2]  # White


class Ui_Dialog(object):
    def calcuateAccuracy(self):
        global headlinesDisplayedCounter
        headlinesDisplayedCounter = 0
        global wrongScoreCounter
        wrongScoreCounter = 0
        global calculatingAccuracy
        calculatingAccuracy = True
        global allHeadlinesShown
        allHeadlinesShown = False
        global lineNumber
        lineNumber = 0

        self.checkBox1.show()
        self.checkBox2.show()
        self.checkBox3.show()
        self.checkBox4.show()
        self.accuracyLabel.show()
        self.nextFourHeadlines()

    def noteCheckData(self):
        global wrongScoreCounter
        global displayingfile
        global displayingHeadlines
        global displayingScores

        with open(displayingfile[:-20] + "wrongHeadlines.txt",
                  mode="a") as wrongHeadlines:  # To store incorrect headlines and scores
            try:
                if self.checkBox1.isChecked():
                    wrongScoreCounter += 1
                    wrongHeadlines.write(displayingHeadlines[0] + ">>" + displayingScores[0] + "\n")
                    self.checkBox1.setChecked(False)
                if self.checkBox2.isChecked():
                    wrongScoreCounter += 1
                    wrongHeadlines.write(displayingHeadlines[1] + ">>" + displayingScores[1] + "\n")
                    self.checkBox2.setChecked(False)
                if self.checkBox3.isChecked():
                    wrongScoreCounter += 1
                    wrongHeadlines.write(displayingHeadlines[2] + ">>" + displayingScores[2] + "\n")
                    self.checkBox3.setChecked(False)
                if self.checkBox4.isChecked():
                    wrongScoreCounter += 1
                    wrongHeadlines.write(displayingHeadlines[3] + ">>" + displayingScores[3] + "\n")
                    self.checkBox4.setChecked(False)
            except:
                pass

    def nextFourHeadlines(self):
        global wrongScoreCounter
        global headlinesDisplayedCounter
        global calculatingAccuracy
        global displayingfile
        global calculatingAccuracy
        global allHeadlinesShown
        global lineNumber

        if calculatingAccuracy:
            self.noteCheckData()

        if allHeadlinesShown and calculatingAccuracy:
            accuracy = "{0:.2f}".format(
                ((headlinesDisplayedCounter - wrongScoreCounter) / headlinesDisplayedCounter) * 100) + "%"
            self.accuracyResultLabel.setText(_fromUtf8(
                "<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:600; color: #20ee94;\">\
                <u>Accuracy </u>" + accuracy + "</span></p></body></html>"))
            self.accuracyResultLabel.show()
            self.checkBox1.hide()
            self.checkBox2.hide()
            self.checkBox3.hide()
            self.checkBox4.hide()
            self.accuracyLabel.hide()
            file_to_store_accuracy = displayingfile[:-20] + "accuracy.txt"
            with open(file_to_store_accuracy, "w") as f:
                f.write(accuracy)
            calculatingAccuracy = False
            return

        with open(displayingfile, "r") as f:
            data = f.readlines()[lineNumber:lineNumber + 9]
            data1 = data[:8:2]  # line 1-8 in increment of 2 since 2nd line has scores
            data2 = data[1:9:2]  # line 2-9 in increment of 2 since 1st line has headlines
            for i, line in enumerate(data1):  # Remove \n from headlines
                temp = line[:-1]
                data1[i] = temp

            for i, line in enumerate(data2):  # Remove >> and \n from scores
                temp = line[3:8]
                if temp[0] != "-":
                    temp = " " + temp
                data2[i] = temp

            lineNumber += 8
            global displayingHeadlines
            global displayingScores
            displayingHeadlines.clear()
            displayingScores.clear()
            displayingHeadlines = data1
            displayingScores = data2

            try:
                color = headline_display_color(float(displayingScores[0]))
                self.Headline1.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                         color:" + color + ";\"><b>" + displayingHeadlines[0] + "</b></span></p></body></html>",
                                                  None))
                self.Value1.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                         color:" + color + ";\"><b>" + displayingScores[0] + "</b></span></p></body></html>", None))
                headlinesDisplayedCounter += 1

            except IndexError:
                self.Headline1.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                         color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                                  None))
                self.Value1.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                         color:" + ";\"><b>" + "" + "</b></span></p></body></html>", None))
                self.checkBox1.hide()
                allHeadlinesShown = True

            try:
                color = headline_display_color(float(displayingScores[1]))
                self.Headline2.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                    color:" + color + ";\"><b>" + displayingHeadlines[
                    1] + "</b></span></p></body></html>",
                                                  None))
                self.Value2.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                    color:" + color + ";\"><b>" + displayingScores[1] + "</b></span></p></body></html>",
                                               None))
                headlinesDisplayedCounter += 1
            except:
                self.Headline2.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                                  None))
                self.Value2.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                               None))
                self.checkBox2.hide()
                allHeadlinesShown = True

            try:
                color = headline_display_color(float(displayingScores[2]))
                self.Headline3.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                    color:" + color + ";\"><b>" + displayingHeadlines[
                    2] + "</b></span></p></body></html>",
                                                  None))
                self.Value3.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                    color:" + color + ";\"><b>" + displayingScores[2] + "</b></span></p></body></html>",
                                               None))
                headlinesDisplayedCounter += 1
            except:
                self.Headline3.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                                  None))
                self.Value3.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                               None))
                self.checkBox3.hide()
                allHeadlinesShown = True

            try:
                color = headline_display_color(float(displayingScores[3]))
                self.Headline4.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                    color:" + color + ";\"><b>" + displayingHeadlines[
                    3] + "</b></span></p></body></html>",
                                                  None))
                self.Value4.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                    color:" + color + ";\"><b>" + displayingScores[3] + "</b></span></p></body></html>",
                                               None))
                headlinesDisplayedCounter += 1
            except:
                self.Headline4.setText(_translate("Dialog", "<html><head/><body><p align=\"justify\"><span style=\" font-size:12pt;\
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                                  None))
                self.Value4.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; \
                                                    color:" + ";\"><b>" + "" + "</b></span></p></body></html>",
                                               None))
                self.checkBox4.hide()
                allHeadlinesShown = True

    def oneWeekAnalysis(self):  # Graph plot for 1 week scores
        pg.setConfigOptions(antialias=True)
        global displayingfile
        global outputDate
        today = outputDate  # Get output date, compute 1 week from that date

        y_axis_pos = []
        x_axis_pos = []
        y_axis_neg = []
        x_axis_neg = []
        y_axis_zero = []
        x_axis_zero = []
        line_counter = 0
        for i in range(0, 7):
            temp = displayingfile[:-31]
            weekDate = today - timedelta(days=i)
            temp += str(weekDate) + "\\" + str(weekDate) + "scores.txt"
            try:
                with open(temp, "r") as f:
                    for line in f:
                        if line.startswith(">>"):
                            num = float(line[3:].rstrip("\n"))
                            line_counter += 1
                            if num > 0:
                                y_axis_pos.append(num)
                                x_axis_pos.append(line_counter)
                            if num < 0:
                                y_axis_neg.append(num)
                                x_axis_neg.append(line_counter)
                            if num == 0:
                                y_axis_zero.append(num)
                                x_axis_zero.append(line_counter)
                line_counter += 1
            except FileNotFoundError:  # If data does not exists, ignore
                continue

        self.Graph.plotItem.clear()  # reset graph
        self.Graph.plot(x_axis_pos, y_axis_pos, pen=(200, 200, 200), symbolBrush=(0, 255, 0), symbolPen='r')
        self.Graph.plot(x_axis_neg, y_axis_neg, pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='b')
        self.Graph.plot(x_axis_zero, y_axis_zero, pen=(0, 0, 0), symbolBrush=(255, 255, 255), symbolPen='k')

    def dateSelected(self):
        # Turn Off accuracy calculation mode before displaying output
        global headlinesDisplayedCounter
        headlinesDisplayedCounter = 0
        global wrongScoreCounter
        wrongScoreCounter = 0
        self.checkBox1.hide()
        self.checkBox2.hide()
        self.checkBox3.hide()
        self.checkBox4.hide()
        self.accuracyLabel.hide()
        self.accuracyResultLabel.hide()
        global calculatingAccuracy
        calculatingAccuracy = False
        global allHeadlinesShown
        allHeadlinesShown = False
        #########################################

        x = self.calendarWidget.selectedDate()
        day = x.day()
        month = x.month()
        year = x.year()
        if day < 10:  # since we get 1,2,3,4...instead of 01,02,03...
            day = "0" + str(day)
        if month < 10:
            month = "0" + str(month)

        selected_date = str(year) + "-" + str(month) + "-" + str(day)
        global outputDate
        outputDate = date(int(year), int(month), int(day))  # Set selected date as output data
        global displayingfile
        displayingfile = displayingfile[:-31]  # remove previous dates from file location name
        displayingfile += selected_date + "\\" + selected_date + "scores.txt"

        my_file = Path(displayingfile)
        if my_file.is_file():  # if file exists for selected date
            self.Graph.plotItem.clear()  # reset graph
            makeGraph(self.Graph)

            drawWordCloud()
            self.wordCloud.setPixmap(QtGui.QPixmap("./data/wc.png"))
            # self.wordCloud.setPixmap(QtGui.QPixmap("../data/wc.png"))  #testing

            global lineNumber
            lineNumber = 0
            self.nextFourHeadlines()

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(1355, 696)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon/Project/HeadlineMining Gitlab/images/icon.ico")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setAutoFillBackground(False)
        Dialog.setStyleSheet(_fromUtf8("background-image: url(:/bavkground/images/woodback.jpg);"))

        # Graph
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOption('leftButtonPan', False)
        self.Graph = PlotWidget(Dialog)
        self.Graph.setGeometry(QtCore.QRect(670, 30, 651, 321))
        self.Graph.setObjectName(_fromUtf8("Graph"))
        makeGraph(self.Graph)

        # Graph Label
        self.GraphLabel = QtGui.QLabel(Dialog)
        self.GraphLabel.setGeometry(QtCore.QRect(670, 1, 651, 28))
        self.GraphLabel.setAutoFillBackground(False)
        self.GraphLabel.setStyleSheet(_fromUtf8("background:transparent;"))
        self.GraphLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.GraphLabel.setText(_fromUtf8(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color:#fff2af;\"><u>Opinion Graph Of Headlines</u></span></p></body></html>"))
        self.GraphLabel.setTextFormat(QtCore.Qt.RichText)
        self.GraphLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.GraphLabel.setWordWrap(True)
        self.GraphLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.GraphLabel.setObjectName(_fromUtf8("GraphLabel"))

        # wordCloud
        self.wordCloud = pic = QtGui.QLabel(Dialog)
        self.wordCloud.setGeometry(QtCore.QRect(40, 30, 560, 321))
        self.wordCloud.setObjectName(_fromUtf8("wordCloud"))
        drawWordCloud()
        self.wordCloud.setPixmap(QtGui.QPixmap("./data/wc.png"))
        # self.wordCloud.setPixmap(QtGui.QPixmap("../data/wc.png")) #testing

        # WordCloud Label
        self.WordCloudLabel = QtGui.QLabel(Dialog)
        self.WordCloudLabel.setGeometry(QtCore.QRect(40, 1, 560, 28))
        self.WordCloudLabel.setAutoFillBackground(False)
        self.WordCloudLabel.setStyleSheet(_fromUtf8("background:transparent;"))
        self.WordCloudLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.WordCloudLabel.setText(_fromUtf8(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color:#fff2af;\">\
            <u>Hot Topics Based On Usage Frequency In Headlines</u></span></p></body></html>"))
        self.WordCloudLabel.setTextFormat(QtCore.Qt.RichText)
        self.WordCloudLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.WordCloudLabel.setWordWrap(True)
        self.WordCloudLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.WordCloudLabel.setObjectName(_fromUtf8("WordCloudLabel"))

        # Calender
        self.calendarWidget = QtGui.QCalendarWidget(Dialog)
        self.calendarWidget.setGeometry(QtCore.QRect(830, 430, 361, 251))
        self.calendarWidget.setMinimumDate(QtCore.QDate(2017, 1, 2))
        self.calendarWidget.setMaximumDate(QtCore.QDate(2017, 12, 31))
        self.calendarWidget.setObjectName(_fromUtf8("calendarWidget"))
        self.calendarWidget.clicked.connect(self.dateSelected)

        # Calender Label
        self.CalenderLabel = QtGui.QLabel(Dialog)
        self.CalenderLabel.setGeometry(QtCore.QRect(760, 370, 491, 51))
        self.CalenderLabel.setAutoFillBackground(False)
        self.CalenderLabel.setStyleSheet(_fromUtf8("background:transparent;"))
        self.CalenderLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.CalenderLabel.setText(_fromUtf8(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color:#fff2af;\"><u>Select a date from calender below to change day</u></span></p></body></html>"))
        self.CalenderLabel.setTextFormat(QtCore.Qt.RichText)
        self.CalenderLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CalenderLabel.setWordWrap(True)
        self.CalenderLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.CalenderLabel.setObjectName(_fromUtf8("CalenderLabel"))

        # Nextbutton
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(670, 490, 81, 81))
        self.pushButton.setStyleSheet(_fromUtf8("background-image: url(:/labelBackground/images/nextButton.png);\n"
                                                "border:none;"))
        self.pushButton.setAutoDefault(True)
        self.pushButton.isCheckable()
        self.pushButton.setDefault(False)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton.clicked.connect(self.nextFourHeadlines)

        # WeeklyButton
        self.weekButton = QtGui.QPushButton(Dialog)
        self.weekButton.setGeometry(QtCore.QRect(1210, 490, 130, 81))
        self.weekButton.setStyleSheet(_fromUtf8("color:white; font-size:14pt; font-weight:600; background:grey; \
                                                 font-family:'Lucida Calligraphy';border-style: outset;\
                                                 border-width: 2px;border-radius: 15px;border-color: black;\
                                                padding: 4px;"))
        self.weekButton.setAutoDefault(True)
        self.weekButton.isCheckable()
        self.weekButton.setText("One Week \nAnalysis")
        self.weekButton.setObjectName(_fromUtf8("weekButton"))
        self.weekButton.clicked.connect(self.oneWeekAnalysis)

        # Calculate accuracy button
        self.accuracyButton = QtGui.QPushButton(Dialog)
        self.accuracyButton.setGeometry(QtCore.QRect(1210, 591, 130, 81))
        self.accuracyButton.setStyleSheet(_fromUtf8("color:white; font-size:14pt; font-weight:600; background:grey; \
                                                         font-family:'Lucida Calligraphy';border-style: outset;\
                                                         border-width: 2px;border-radius: 15px;border-color: black;\
                                                        padding: 4px;"))
        self.accuracyButton.setAutoDefault(True)
        self.accuracyButton.isCheckable()
        self.accuracyButton.setText("Calculate \n Accuracy ")
        self.accuracyButton.setObjectName(_fromUtf8("accuracyButton"))
        self.accuracyButton.clicked.connect(self.calcuateAccuracy)

        # Accuracy instruction label
        self.accuracyLabel = QtGui.QLabel(Dialog)
        self.accuracyLabel.setGeometry(QtCore.QRect(30, 370, 521, 28))
        self.accuracyLabel.setAutoFillBackground(False)
        self.accuracyLabel.setStyleSheet(_fromUtf8("background:transparent;"))
        self.accuracyLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.accuracyLabel.setText(_fromUtf8(
            "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600; color: #20ee94;\">\
            <u>Cycle through all headlines and select incorrect scores</u></span></p></body></html>"))
        self.accuracyLabel.setTextFormat(QtCore.Qt.RichText)
        self.accuracyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.accuracyLabel.setWordWrap(True)
        self.accuracyLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.accuracyLabel.setObjectName(_fromUtf8("accuracyLabel"))
        self.accuracyLabel.hide()

        # AccuracyResult Label
        self.accuracyResultLabel = QtGui.QLabel(Dialog)
        self.accuracyResultLabel.setGeometry(QtCore.QRect(645, 591, 150, 100))  # 670, 490, 81, 81
        self.accuracyResultLabel.setAutoFillBackground(False)
        self.accuracyResultLabel.setStyleSheet(_fromUtf8("background:transparent;"))
        self.accuracyResultLabel.setFrameShadow(QtGui.QFrame.Plain)
        self.accuracyResultLabel.setTextFormat(QtCore.Qt.RichText)
        self.accuracyResultLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.accuracyResultLabel.setWordWrap(True)
        self.accuracyResultLabel.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.accuracyResultLabel.setObjectName(_fromUtf8("accuracyResultLabel"))
        self.accuracyResultLabel.hide()

        # checkboxes
        self.checkBox1 = QtGui.QCheckBox(Dialog)
        self.checkBox1.setGeometry(QtCore.QRect(15, 408, 16, 17))
        self.checkBox1.setText(_fromUtf8(""))
        self.checkBox1.setObjectName(_fromUtf8("checkBox1"))
        self.checkBox1.hide()

        self.checkBox2 = QtGui.QCheckBox(Dialog)
        self.checkBox2.setGeometry(QtCore.QRect(15, 488, 16, 17))
        self.checkBox2.setText(_fromUtf8(""))
        self.checkBox2.setObjectName(_fromUtf8("checkBox2"))
        self.checkBox2.hide()

        self.checkBox3 = QtGui.QCheckBox(Dialog)
        self.checkBox3.setGeometry(QtCore.QRect(15, 568, 16, 17))
        self.checkBox3.setText(_fromUtf8(""))
        self.checkBox3.setObjectName(_fromUtf8("checkBox3"))
        self.checkBox3.hide()

        self.checkBox4 = QtGui.QCheckBox(Dialog)
        self.checkBox4.setGeometry(QtCore.QRect(15, 648, 16, 17))
        self.checkBox4.setText(_fromUtf8(""))
        self.checkBox4.setObjectName(_fromUtf8("checkBox4"))
        self.checkBox4.hide()

        # Headline labels
        self.Headline1 = QtGui.QLabel(Dialog)
        self.Headline1.setGeometry(QtCore.QRect(40, 392, 521, 51))
        self.Headline1.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Headline1.setTextFormat(QtCore.Qt.RichText)
        self.Headline1.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.Headline1.setWordWrap(True)
        self.Headline1.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Headline1.setObjectName(_fromUtf8("Headline1"))

        self.Headline2 = QtGui.QLabel(Dialog)
        self.Headline2.setGeometry(QtCore.QRect(40, 472, 521, 51))
        self.Headline2.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Headline2.setTextFormat(QtCore.Qt.RichText)
        self.Headline2.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.Headline2.setWordWrap(True)
        self.Headline2.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Headline2.setObjectName(_fromUtf8("Headline2"))

        self.Headline3 = QtGui.QLabel(Dialog)
        self.Headline3.setGeometry(QtCore.QRect(40, 552, 521, 51))
        self.Headline3.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Headline3.setTextFormat(QtCore.Qt.RichText)
        self.Headline3.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.Headline3.setWordWrap(True)
        self.Headline3.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Headline3.setObjectName(_fromUtf8("Headline3"))

        self.Headline4 = QtGui.QLabel(Dialog)
        self.Headline4.setGeometry(QtCore.QRect(40, 632, 521, 51))
        self.Headline4.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Headline4.setTextFormat(QtCore.Qt.RichText)
        self.Headline4.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
        self.Headline4.setWordWrap(True)
        self.Headline4.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Headline4.setObjectName(_fromUtf8("Headline4"))

        # Score Labels
        self.Value4 = QtGui.QLabel(Dialog)
        self.Value4.setGeometry(QtCore.QRect(580, 632, 71, 51))
        self.Value4.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Value4.setTextFormat(QtCore.Qt.RichText)
        self.Value4.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignLeft)
        self.Value4.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Value4.setObjectName(_fromUtf8("Value4"))

        self.Value3 = QtGui.QLabel(Dialog)
        self.Value3.setGeometry(QtCore.QRect(580, 552, 71, 51))
        self.Value3.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Value3.setTextFormat(QtCore.Qt.RichText)
        self.Value3.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignLeft)
        self.Value3.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Value3.setObjectName(_fromUtf8("Value3"))

        self.Value2 = QtGui.QLabel(Dialog)
        self.Value2.setGeometry(QtCore.QRect(580, 472, 71, 51))
        self.Value2.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Value2.setTextFormat(QtCore.Qt.RichText)
        self.Value2.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignLeft)
        self.Value2.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Value2.setObjectName(_fromUtf8("Value2"))

        self.Value1 = QtGui.QLabel(Dialog)
        self.Value1.setGeometry(QtCore.QRect(580, 392, 71, 51))
        self.Value1.setStyleSheet(_fromUtf8("background:transparent;"))
        self.Value1.setTextFormat(QtCore.Qt.RichText)
        self.Value1.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignLeft)
        self.Value1.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.Value1.setObjectName(_fromUtf8("Value1"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Analysis Of Extracted Headlines", None))
        self.Headline1.setText(_translate("Dialog",
                                          "<html><head/><body><p align=\"justify\"><span style=\" font-size:10pt; color:#ffffff;\">Headline 1</span></p></body></html>",
                                          None))
        self.Value1.setText(_translate("Dialog",
                                       "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">0.0</span></p></body></html>",
                                       None))
        self.Headline2.setText(_translate("Dialog",
                                          "<html><head/><body><p align=\"justify\"><span style=\" font-size:10pt; color:#ffffff;\">Headline 1</span></p></body></html>",
                                          None))
        self.Headline3.setText(_translate("Dialog",
                                          "<html><head/><body><p align=\"justify\"><span style=\" font-size:10pt; color:#ffffff;\">Headline 1</span></p></body></html>",
                                          None))
        self.Headline4.setText(_translate("Dialog",
                                          "<html><head/><body><p align=\"justify\"><span style=\" font-size:10pt; color:#ffffff;\">Headline 1</span></p></body></html>",
                                          None))
        self.Value4.setText(_translate("Dialog",
                                       "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">0.0</span></p></body></html>",
                                       None))
        self.Value3.setText(_translate("Dialog",
                                       "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">0.0</span></p></body></html>",
                                       None))
        self.Value2.setText(_translate("Dialog",
                                       "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; color:#ffffff;\">0.0</span></p></body></html>",
                                       None))


def showOutput():  # testing: add parameter : file
    global displayingfile
    displayingfile = sys.argv[1]  # Take scores file as command line argument #testing
    # displayingfile = file  # testing
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    ui.nextFourHeadlines()
    Dialog.show()
    app.processEvents()
    sys.exit(app.exec_())


if __name__ == "__main__":
    showOutput()
    # for testing purpose
    # import os

    # os.chdir("../")
    # showOutput(
    #    r'C:\Users\Kuldeep\Desktop\Project\HeadlineMining Gitlab\data\googleNews\2017-03-21\2017-03-21scores.txt')
