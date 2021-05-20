# Tomasz Walburg 176050, AiR KSD

import sys
import math
import copy
import random
import os
import socket
import threading
from datetime import datetime
from PySide2.QtWidgets import *
from PySide2.QtGui import QPen, QPainter, QPolygonF, QBrush, QTextCursor, QFont, QPalette, QImage, QColor
from PySide2.QtCore import Qt, QPointF, QPropertyAnimation, QEvent, QRectF, QObject, Signal, QStringListModel
from xml.dom import minidom
import xml.etree.ElementTree as ET


# klasa posiadajaca dane wierzcholkow kazdego pola oraz nr kolumny oraz pozycje w kolumnie
class Plansza():
    count = 0

    def __init__(self, x0, x1, x2, x3, x4, x5, y0, y1, y2, y3, y4, y5, kolumna, nr_w_kol):
        self.x0 = x0
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.x4 = x4
        self.x5 = x5
        self.y0 = y0
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.y4 = y4
        self.y5 = y5
        self.kolumna = kolumna
        self.nr_w_kol = nr_w_kol
        self.zajety = False
        self.count = Plansza.count
        self.srodek_x = (self.x0 + self.x3) / 2
        self.srodek_y = (self.y0 + self.y3) / 2
        Plansza.count += 1


# glowne okno gry wraz z plansza
class Window(QMainWindow):
    def __init__(self, grid_size):
        super().__init__()
        self.grid_size = grid_size                  # rozmiar planszy
        self.var = 2 * self.grid_size - 1               # ilosc kolumn planszy
        self.pola = []
        self.pola2 = []
        self.il_pol = 0
        self.il_pol2 = 0
        self.iks = 0
        self.igr = 0
        self.wynik = 0                      # aktualny wynik gracza
        self.szerokosc_sceny = self.var * ((85.98076211353315 + math.sqrt(3) / 2 * 60) - (34.01923788646684 + math.sqrt(3) / 2 * 60))
        self.wysokosc_sceny = self.var * ((115.98076211353315 + math.sqrt(3) / 4 + 43) - (60 + math.sqrt(3) / 4 + 43))
        self.ruchy = []
        self.dodane = []
        self.wartosc = []

        self.setWindowTitle("Hexagonal 2048, enjoy!")

        self.buttonpg = QPushButton(self)           # stworzenie przyciskow do sterowania agentami
        self.buttonp = QPushButton(self)
        self.buttonpd = QPushButton(self)
        self.buttonld = QPushButton(self)
        self.buttonl = QPushButton(self)
        self.buttonlg = QPushButton(self)

        self.text_box = QTextEdit(self)             # stworzenie textboxa

        self.label1 = QLabel(self)                  # stworzenie labeli do wypisywania aktualnych wynikow
        self.label2 = QLabel(self)
        self.label3 = QLabel(self)
        self.label4 = QLabel(self)

        self._createActions()               # stworzenie menuBar i jego akcji
        self._connectActions()
        self._createMenuBar()

        self.scene = QGraphicsScene(self)           # scena gracza nr1

        self.scene2 = QGraphicsScene(self)              # scena gracza nr2

        self.create_ui()                    # stworzenie siatek na obu scenach

        self.view = QGraphicsView(self.scene, self)

        self.view2 = QGraphicsView(self.scene2, self)

        self.properties()               # ustawienie wlasciwosci elementow programu

        self.fields = [Field(self.pola, self, self.grid_size)]
        self.dodane.append(self.fields[-1].nmb)
        self.wartosc.append(self.fields[-1].value)
        self.fields.append(Field(self.pola, self, self.grid_size))
        self.dodane.append(self.fields[-1].nmb)
        self.wartosc.append(self.fields[-1].value)

        self.show()

    def properties(self):                           # wlasciwosci przyciskow/textboxow/sceny
        self.setGeometry(500, 200, self.szerokosc_sceny * 3, self.wysokosc_sceny + 200)
        self.setStyleSheet("background-color: #464241;")

        self.buttonpg.setText("Prawa\n gora")
        self.buttonpg.setFixedHeight(50)
        self.buttonpg.setFixedWidth(50)
        self.buttonpg.move(55, self.wysokosc_sceny * 1.02)
        self.buttonpg.setStyleSheet("background-color: #009999")
        self.buttonpg.clicked.connect(self.prawo_g)

        self.buttonp.setText("Prawo")
        self.buttonp.setFixedHeight(50)
        self.buttonp.setFixedWidth(50)
        self.buttonp.move(55, self.wysokosc_sceny * 1.02 + 50)
        self.buttonp.setStyleSheet("background-color: #009999")
        self.buttonp.clicked.connect(self.prawo)

        self.buttonpd.setText("Prawy\n dol")
        self.buttonpd.setFixedHeight(50)
        self.buttonpd.setFixedWidth(50)
        self.buttonpd.move(55, self.wysokosc_sceny * 1.02 + 100)
        self.buttonpd.setStyleSheet("background-color: #009999")
        self.buttonpd.clicked.connect(self.prawo_d)

        self.buttonld.setText("Lewy\n dol")
        self.buttonld.setFixedHeight(50)
        self.buttonld.setFixedWidth(50)
        self.buttonld.move(5, self.wysokosc_sceny * 1.02 + 100)
        self.buttonld.setStyleSheet("background-color: #009999")
        self.buttonld.clicked.connect(self.lewo_d)

        self.buttonl.setText("Lewo")
        self.buttonl.setFixedHeight(50)
        self.buttonl.setFixedWidth(50)
        self.buttonl.move(5, self.wysokosc_sceny * 1.02 + 50)
        self.buttonl.setStyleSheet("background-color: #009999")
        self.buttonl.clicked.connect(self.lewo)

        self.buttonlg.setText("Lewa\n gora")
        self.buttonlg.setFixedHeight(50)
        self.buttonlg.setFixedWidth(50)
        self.buttonlg.move(5, self.wysokosc_sceny * 1.02)
        self.buttonlg.setStyleSheet("background-color: #009999")
        self.buttonlg.clicked.connect(self.lewo_g)

        self.text_box.setGeometry(130, self.wysokosc_sceny * 1.02, 250, 150)
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet("background-color: white")

        self.label1.setText("Punkty gracza 1:")
        self.label1.setGeometry(self.szerokosc_sceny + 40, 50, 100, 30)
        self.label1.setFont(QFont('Arial', 10))

        self.label2.setText(str(self.wynik))
        self.label2.setGeometry(self.szerokosc_sceny + 40, 80, 100, 30)
        self.label2.setFont(QFont('Arial', 10))

        self.label3.setText("Punkty gracza 1:")
        self.label3.setGeometry(self.szerokosc_sceny + 40, 120, 100, 30)
        self.label3.setFont(QFont('Arial', 10))

        self.label4.setText("0")
        self.label4.setGeometry(self.szerokosc_sceny + 40, 150, 100, 30)
        self.label4.setFont(QFont('Arial', 10))

        self.scene.setBackgroundBrush(QBrush(Qt.gray))
        self.scene2.setBackgroundBrush(QBrush(Qt.gray))

        self.view.setAlignment(Qt.AlignTop and Qt.AlignLeft)
        self.view.setGeometry(0, 20, self.wysokosc_sceny, self.szerokosc_sceny)
        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

        self.view2.setAlignment(Qt.AlignTop and Qt.AlignLeft)
        self.view2.setGeometry(500, 20, self.wysokosc_sceny, self.szerokosc_sceny)

        sys.stdout = Stream()                       # czesc przekierowania konsoli do qtextedit
        sys.stdout.box.connect(self.onUpdateText)

    def _createMenuBar(self):
        menuBar = self.menuBar()            # stworzenie paska menu

        editMenu = menuBar.addMenu("&Opcje")                        # dodanie "opcji" do paska menu
        editMenu.addAction(self.dialog)
        editMenu.addAction(self.adres)
        editMenu.addAction(self.port)


        nowaMenu = menuBar.addAction(self.nowa)

        zapiszMenu = menuBar.addAction(self.zapisz)

        emulujMenu = menuBar.addAction(self.emuluj)

        autoMenu = menuBar.addAction(self.auto)

        exitMenu = menuBar.addAction(self.wyjdz)

        menuBar.setStyleSheet("""QMenuBar {
             background-color: gray;
        }""")

    def _createActions(self):                       # stworzenie akcji dla przyciskow w menubox
        self.dialog = QAction("Wybor rozmiaru planszy", self)
        self.adres = QAction("Adres IP")
        self.port = QAction("Port Połącznia")

        self.nowa = QAction("Nowa gra", self)

        self.zapisz = QAction("Zapisz gre", self)

        self.emuluj = QAction("Emuluj", self)

        self.auto = QAction("Autorozgrywka", self)

        self.wyjdz = QAction("&Exit", self)

    def _connectActions(self):                          # obsluga akcji dla przyciskow w menubox
        self.dialog.triggered.connect(self.dialogg)

        self.nowa.triggered.connect(self.nowaa)

        self.zapisz.triggered.connect(self.fileDialogSave)

        self.emuluj.triggered.connect(self.fileDialogRead)

        self.wyjdz.triggered.connect(self.wyjdzz)

    def fileDialogRead(self):                       # odczytywanie stanu gry
        dia = QFileDialog()
        filter = "XML (*.xml)"

        path = QFileDialog.getOpenFileName(dia, "name", "", filter)[0]

        tree = ET.parse(path)
        root = tree.getroot()


        #dia.exec()

    def fileDialogSave(self):                       # zapisywanie stanu gry
        dia, _ = QFileDialog.getSaveFileName(self, "Save file", "history.xml", ".xml")

        root = ET.Element("Save")

        pla1 = ET.Element("gracz1")
        root.append(pla1)

        m2 = ET.SubElement(pla1, "seed")

        h1 = ET.SubElement(m2, "klocek1")
        g1 = ET.SubElement(h1, "wiersz")
        g1.text = str(self.dodane[0][0])
        g2 = ET.SubElement(h1, "kolumna")
        g2.text = str(self.dodane[0][1])
        g3 = ET.SubElement(h1, "wartosc")
        g3.text = str(self.wartosc[0])

        h2 = ET.SubElement(m2, "klocek2")
        t1 = ET.SubElement(h2, "wiersz")
        t1.text = str(self.dodane[1][0])
        t2 = ET.SubElement(h2, "kolumna")
        t2.text = str(self.dodane[1][1])
        t3 = ET.SubElement(h2, "wartosc")
        t3.text = str(self.wartosc[1])

        m1 = ET.SubElement(pla1, "ruchy")

        for i in range(len(self.ruchy)):
            b1 = ET.SubElement(m1, f"ruch{i}")
            strona = ET.SubElement(b1, f"strona{i}")
            strona.text = self.ruchy[i]
            wiersz = ET.SubElement(b1, f"wiersz{i}")
            wiersz.text = str(self.dodane[i+2][0])
            kolumna = ET.SubElement(b1, f"kolumna{i}")
            kolumna.text = str(self.dodane[i + 2][1])
            wartosc = ET.SubElement(b1, f"wartosc{i}")
            wartosc.text = str(self.wartosc[i+2])

        tree = ET.ElementTree(root)
        try:
            tree.write(dia)
        except:
            pass

    def dialogg(self):                  # DialogBox do zmiany rozmiaru planszy
        d = QDialog()
        d.setWindowTitle("Wybierz rozmiar")
        d.setGeometry(700,400, 250, 100)

        b4 = QPushButton("Zamknij", d)
        b4.move(150, 40)
        b4.clicked.connect(d.close)

        b1 = QPushButton("3x3x3", d)
        b1.setFont(QFont('Arial', 10))
        b1.move(50, 10)
        b1.clicked.connect(self.trzyy)

        b2 = QPushButton("4x4x4", d)
        b2.setFont(QFont('Arial', 10))
        b2.move(50, 40)
        b2.clicked.connect(self.czteryy)

        b3 = QPushButton("5x5x5", d)
        b3.move(50, 70)
        b3.setFont(QFont('Arial', 10))
        b3.clicked.connect(self.piecc)

        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()

    def nowaa(self):                            # nowa gra
        self.zmien()

    def wyjdzz(self):                           # wyjscie z programu
        exit()

    def zmien(self):                            # zmiana rozmiaru planszy
        self.var = 2 * self.grid_size - 1
        self.pola.clear()
        self.il_pol = 0
        self.wynik = 0
        self.iks = 0
        self.igr = 0
        self.szerokosc_sceny = self.var * (
                (85.98076211353315 + math.sqrt(3) / 2 * 60) - (34.01923788646684 + math.sqrt(3) / 2 * 60))
        self.wysokosc_sceny = self.var * ((115.98076211353315 + math.sqrt(3) / 4 + 43) - (60 + math.sqrt(3) / 4 + 43))
        self.ruchy.clear()
        self.dodane.clear()
        self.wartosc.clear()

        self.setGeometry(500, 200, self.szerokosc_sceny * 3, self.wysokosc_sceny+200)

        self.buttonpg.move(55, self.wysokosc_sceny * 1.02)
        self.buttonp.move(55, self.wysokosc_sceny * 1.02 + 50)
        self.buttonpd.move(55, self.wysokosc_sceny * 1.02 + 100)
        self.buttonld.move(5, self.wysokosc_sceny * 1.02 + 100)
        self.buttonl.move(5, self.wysokosc_sceny * 1.02 + 50)
        self.buttonlg.move(5, self.wysokosc_sceny * 1.02)

        self.text_box.setGeometry(130, self.wysokosc_sceny * 1.02, 250, 150)

        self.label1.setGeometry(self.szerokosc_sceny+40, 50, 100, 30)
        self.label2.setGeometry(self.szerokosc_sceny+40, 80, 100, 30)
        self.label3.setGeometry(self.szerokosc_sceny + 40, 120, 100, 30)
        self.label4.setGeometry(self.szerokosc_sceny + 40, 150, 100, 30)

        self.label2.setText("0")
        self.label4.setText("0")

        self.scene.clear()
        if self.grid_size == 3:
            self.scene.setSceneRect(-21.296388, 56.645898, 266.515825, 236.421017)
        elif self.grid_size == 4:
            self.scene.setSceneRect(-47.277150, 56.645898, 370.438874, 323.287042)
        elif self.grid_size == 5:
            self.scene.setSceneRect(-73.257913, 56.645898, 474.361922, 410.153068)

        self.scene2.clear()
        if self.grid_size == 3:
            self.scene2.setSceneRect(-21.296388, 56.645898, 266.515825, 236.421017)
        elif self.grid_size == 4:
            self.scene2.setSceneRect(-47.277150, 56.645898, 370.438874, 323.287042)
        elif self.grid_size == 5:
            self.scene2.setSceneRect(-73.257913, 56.645898, 474.361922, 410.153068)

        self.create_ui()

        self.view.setGeometry(0, 20, self.wysokosc_sceny, self.szerokosc_sceny)
        self.view2.setGeometry(self.szerokosc_sceny * 3-(self.szerokosc_sceny+10), 20, self.wysokosc_sceny, self.szerokosc_sceny)

        self.fields.clear()
        self.fields = [Field(self.pola, self, self.grid_size)]
        self.dodane.append(self.fields[-1].nmb)
        self.wartosc.append(self.fields[-1].value)
        self.fields.append(Field(self.pola, self, self.grid_size))
        self.dodane.append(self.fields[-1].nmb)
        self.wartosc.append(self.fields[-1].value)

        self.text_box.clear()

    def trzyy(self):                        # zmiana rozmiaru planszy na 3x3x3
        if self.grid_size != 3:
            self.grid_size = 3
            self.zmien()

    def czteryy(self):                      # zmiana rozmiaru planszy na 4x4x4
        if self.grid_size != 4:
            self.grid_size = 4
            self.zmien()

    def piecc(self):                        # zmiana rozmiaru planszy na 5x5x5
        if self.grid_size != 5:
            self.grid_size = 5
            self.zmien()


    def eventFilter(self, source, event):               # obsluga gestow myszy
        if event.type() == QEvent.MouseButtonPress:
            x = event.x()
            y = event.y()
            if event.button() == Qt.LeftButton and event.x() >= 0 and event.y() >= 0 and x <= self.wysokosc_sceny and y <= self.szerokosc_sceny:
                self.iks = event.x()
                self.igr = event.y()
        elif event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                x = event.x()
                y = event.y()
                if x> self.iks and y > self.igr + 20:
                    self.prawo_d()
                elif x > self.iks and y < self.igr - 20:
                    self.prawo_g()
                elif x < self.iks and y > self.igr + 20:
                    self.lewo_d()
                elif x < self.iks and y < self.igr - 20:
                    self.lewo_g()
                elif x < self.iks:
                    self.lewo()
                elif x > self.iks:
                    self.prawo()

        return super(Window, self).eventFilter(source, event)

    def prawo_g(self):                  # ruch prawo gora
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var,
                         self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.prawo_g()
        self.akt()
        self.ruchy.append("prawo_g")

    def prawo(self):                    # ruch prawo
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var,
                         self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.prawo()
        self.akt()
        self.ruchy.append("prawo")

    def prawo_d(self):                  # ruch prawo dol
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var,
                         self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.prawo_d()
        self.akt()
        self.ruchy.append("prawo_d")

    def lewo_d(self):                   # ruch lewo dol
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var,
                         self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.lewo_d()
        self.akt()
        self.ruchy.append("lewo_d")

    def lewo(self):                     # ruch lewo
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var,
                         self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.lewo()
        self.akt()
        self.ruchy.append("lewo")

    def lewo_g(self):                   # ruch lewo gora
        lew = Poruszanie(self.grid_size, self.pola, self.fields, self.scene, self.view, self.il_pol, self.var, self.text_box, self.wynik, self.dodane, self.wartosc)
        self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc = lew.lewo_g()
        self.akt()
        self.ruchy.append("lewo_g")

    def create_ui(self):            # stworzenie siatki
        ui1 = Siatka(self.grid_size, self.var, self.scene, self.pola, self.il_pol)
        self.scene, self.pola, self.il_pol = ui1.stworz_plansze()

        ui2 = Siatka(self.grid_size, self.var, self.scene2, self.pola2, self.il_pol2)
        self.scene2, self.pola2, self.il_pol2 = ui2.stworz_plansze()

    def add_pol(self, item):                        # dodanie pola
        self.scene.addItem(item)

    def del_pol(self, item):                        # usuniecie pola
        self.scene.removeItem(item)

    def akt(self):                                  # aktualizacja wyniku gracza
        self.label2.setText(str(self.wynik))

    def onUpdateText(self, text):                   # przekierowanie konsoli na kontrolke QTextEdit
        cursor = self.text_box.textCursor()
        cursor.movePosition(QTextCursor.End)
        text = text.replace("\033[95m", "")
        text = text.replace("\033[0m", "")
        cursor.insertText(text)
        self.text_box.setTextCursor(cursor)
        self.text_box.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__


class Poruszanie():                 # klasa do poruszania agentami
    def __init__(self, grid_size, pola, fields, scene, view, il_pol, var, text_box, wynik, dodane, wartosc):
        self.grid_size = grid_size
        self.pola = pola
        self.fields = fields
        self.scene = scene
        self.view = view
        self.il_pol = il_pol
        self.var = var
        self.text_box = text_box
        self.wynik = wynik
        self.dodane = dodane
        self.wartosc = wartosc

    def prawo_g(self):
        sort_y = self.sort_y()
        zm = False
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_pg()
            if czy_zmienil == True:
                zm = True

        dele = []
        for i in range(len(sort_y)):
            for j in range(len(self.fields)):
                if sort_y[i][1] != j:
                    if self.fields[sort_y[i][1]].nmb[0] < self.grid_size and self.fields[j].nmb[0] < self.grid_size and self.fields[sort_y[i][1]].value == self.fields[j].value and \
                            self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] - 1 and self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] and sort_y[i][1] not in dele:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
                    elif self.fields[j].nmb[0] > self.grid_size - 1 and self.fields[sort_y[i][1]].value == self.fields[j].value and sort_y[i][1] not in dele \
                        and self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] - 1 and self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] + 1:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_y = self.sort_y()
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_pg()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def prawo(self):
        sort_x = self.sort_x_re()
        zm = False
        for i in range(len(sort_x)):
            czy_zmienil = self.fields[sort_x[i][1]].zmien_pozycje_p()
            if czy_zmienil == True:
                zm = True
        dele = []
        for i in range(len(sort_x)):
            for j in range(len(self.fields)):
                if sort_x[i][1] != j and self.fields[sort_x[i][1]].nmb[0] == self.fields[j].nmb[0] and self.fields[sort_x[i][1]].nmb[1] == self.fields[j].nmb[1] + 1 and self.fields[sort_x[i][1]].value == self.fields[j].value and sort_x[i][1] not in dele:
                    self.fields[sort_x[i][1]].value = self.fields[sort_x[i][1]].value * 2
                    self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                    self.del_pol(self.fields[j].fld)
                    wart = self.fields[sort_x[i][1]].upd_text()
                    self.wynik = self.wynik + wart
                    dele.append(j)
                    zm = True
        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_x = self.sort_x_re()
        for i in range(len(sort_x)):
            czy_zmienil = self.fields[sort_x[i][1]].zmien_pozycje_p()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def prawo_d(self):
        sort_y = self.sort_y_re()
        zm = False
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_pd()
            if czy_zmienil == True:
                zm = True

        dele = []
        for i in range(len(sort_y)):
            for j in range(len(self.fields)):
                if sort_y[i][1] != j:
                    if self.fields[sort_y[i][1]].nmb[0] >= self.grid_size-1 and self.fields[j].nmb[0] >= self.grid_size-1 and \
                            self.fields[sort_y[i][1]].value == self.fields[j].value and \
                            self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] + 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] and sort_y[i][1] not in dele:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
                    elif self.fields[j].nmb[0] < self.grid_size-1 and self.fields[sort_y[i][1]].value == self.fields[
                        j].value and sort_y[i][1] not in dele \
                            and self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] + 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] + 1:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True

        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_y = self.sort_y_re()
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_pd()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def lewo_d(self):
        sort_y = self.sort_y_re()
        zm = False
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_ld()
            if czy_zmienil == True:
                zm = True

        dele = []
        for i in range(len(sort_y)):
            for j in range(len(self.fields)):
                if sort_y[i][1] != j:
                    if self.fields[sort_y[i][1]].nmb[0] < self.grid_size and self.fields[j].nmb[
                        0] < self.grid_size and \
                            self.fields[sort_y[i][1]].value == self.fields[j].value and \
                            self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] + 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] and sort_y[i][1] not in dele:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
                    elif self.fields[j].nmb[0] >= self.grid_size-1 and self.fields[sort_y[i][1]].value == self.fields[
                        j].value and sort_y[i][1] not in dele \
                            and self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] + 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] - 1:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_y = self.sort_y_re()
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_ld()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def lewo(self):
        sort_x = self.sort_x()
        zm = False
        for i in range(len(sort_x)):
            czy_zmienil = self.fields[sort_x[i][1]].zmien_pozycje_l()
            if czy_zmienil == True:
                zm = True

        dele = []
        for i in range(len(sort_x)):
            for j in range(len(self.fields)):
                if sort_x[i][1] != j and self.fields[sort_x[i][1]].nmb[0] == self.fields[j].nmb[0] and self.fields[sort_x[i][1]].nmb[1] == \
                        self.fields[j].nmb[1] - 1 and self.fields[sort_x[i][1]].value == self.fields[j].value and sort_x[i][1] not in dele:
                    self.fields[sort_x[i][1]].value = self.fields[sort_x[i][1]].value * 2
                    self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                    self.del_pol(self.fields[j].fld)
                    wart = self.fields[sort_x[i][1]].upd_text()
                    self.wynik = self.wynik + wart
                    dele.append(j)
                    zm = True
        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_x = self.sort_x()
        for i in range(len(sort_x)):
            czy_zmienil = self.fields[sort_x[i][1]].zmien_pozycje_l()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def lewo_g(self):
        sort_y = self.sort_y()
        zm = False
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_lg()
            if czy_zmienil == True:
                zm = True

        dele = []

        for i in range(len(sort_y)):
            for j in range(len(self.fields)):
                if sort_y[i][1] != j:
                    if self.fields[sort_y[i][1]].nmb[0] >= self.grid_size - 1 and self.fields[j].nmb[
                        0] >= self.grid_size - 1 and \
                            self.fields[sort_y[i][1]].value == self.fields[j].value and \
                            self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] - 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] and sort_y[i][1] not in dele:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True
                    elif self.fields[sort_y[i][1]].nmb[0] < self.grid_size - 1 and self.fields[sort_y[i][1]].value == \
                            self.fields[
                                j].value and sort_y[i][1] not in dele \
                            and self.fields[sort_y[i][1]].nmb[0] == self.fields[j].nmb[0] - 1 and \
                            self.fields[sort_y[i][1]].nmb[1] == self.fields[j].nmb[1] - 1:
                        self.fields[sort_y[i][1]].value = self.fields[sort_y[i][1]].value * 2
                        self.pola[self.fields[j].nmb[0]][self.fields[j].nmb[1]].zajety = False
                        self.del_pol(self.fields[j].fld)
                        wart = self.fields[sort_y[i][1]].upd_text()
                        self.wynik = self.wynik + wart
                        dele.append(j)
                        zm = True

        if len(dele) > 0:
            fi = []
            for i in range(len(self.fields)):
                rd = False
                for j in dele:
                    if i != j and rd == False and self.pola[self.fields[i].nmb[0]][
                        self.fields[i].nmb[1]].zajety == True:
                        fi.append(self.fields[i])
                        rd = True
            if len(fi) > 0:
                self.fields.clear()
                self.fields = fi

        sort_y = self.sort_y()
        for i in range(len(sort_y)):
            czy_zmienil = self.fields[sort_y[i][1]].zmien_pozycje_lg()

        if zm == True:
            self.fields.append(Field(self.pola, self, self.grid_size))
            self.dodane.append(self.fields[-1].nmb)
            self.wartosc.append(self.fields[-1].value)
            if len(self.fields) == self.il_pol:
                self.scene.clear()
                self.scene.addText("KONIEC GRY")
                self.view.update()
        self.wypisz()
        return self.grid_size, self.pola, self.fields, self.scene, self.view, self.var, self.text_box, self.wynik, self.dodane, self.wartosc

    def wypisz(self):
        os.system("")
        self.text_box.setPlainText("")
        kolory = ["\033[0m", "\033[95m"]
        for i in range(self.grid_size * 2 - 1):
            x = 0
            if i < self.grid_size - 1:
                x = self.grid_size - i - 1 + (self.var - 2*(i+1))
            elif i >= self.grid_size:
                x = i - self.grid_size + 1 + (2*(i) - self.var)
            x = int(x)
            m = ' '
            print()
            for j in range(len(self.pola[i])):
                if self.pola[i][j].zajety == False:
                    if j == 0 and i == self.grid_size-1:
                        print(f'{str(0):<5}', end=" ")
                    elif j == 0:
                        print(x*m, f'{str(0):<5}', end=" ")
                    else:
                        print(f'{str(0):<5}', end=" ")
                elif self.pola[i][j].zajety == True:
                    for z in range(len(self.fields)):
                        if self.fields[z].nmb[0] == i and self.fields[z].nmb[1] == j:
                            p = self.fields[z].value
                    if j == 0 and i == self.grid_size-1:
                        print(kolory[1] + f'{str(p):<5}', kolory[0], end="")
                    elif j == 0:
                        print(x*m, kolory[1] + f'{str(p):<5}', kolory[0], end="")
                    else:
                        print(kolory[1] + f'{str(p):<5}', kolory[0], end="")
        print()

    def add_pol(self, item):
        self.scene.addItem(item)

    def del_pol(self, item):
        self.scene.removeItem(item)

    def sort_y(self):
        sort_y = []
        for i in range(len(self.fields)):
            nr0, nr1 = self.fields[i].nmb
            sort_y.append([self.pola[nr0][nr1].srodek_y, i])
        sort_y.sort()
        return sort_y

    def sort_x(self):
        sort_x = []
        for i in range(len(self.fields)):
            nr0, nr1 = self.fields[i].nmb
            sort_x.append([self.pola[nr0][nr1].srodek_x, i])
        sort_x.sort()
        return sort_x

    def sort_y_re(self):
        sort_y = []
        for i in range(len(self.fields)):
            nr0, nr1 = self.fields[i].nmb
            sort_y.append([self.pola[nr0][nr1].srodek_y, i])
        sort_y.sort(reverse=True)
        return sort_y

    def sort_x_re(self):
        sort_x = []
        for i in range(len(self.fields)):
            nr0, nr1 = self.fields[i].nmb
            sort_x.append([self.pola[nr0][nr1].srodek_x, i])
        sort_x.sort(reverse=True)
        return sort_x


class Siatka():         # klasa tworzaca siatke
    def __init__(self, grid_size, var, scena, pola, il_pol):
        self.grid_size = grid_size
        self.var = var
        self.scene = scena
        self.pola = pola
        self.il_pol = il_pol

    def stworz_plansze(self):
        blackPen = QPen(Qt.black)
        blackPen.setWidth(5)

        grid_size = self.grid_size
        var = self.var
        x = [60, 85.98076211353315, 85.98076211353315, 60, 34.01923788646684, 34.01923788646684, 60]
        y = [60, 72.99038105676658, 102.99038105676658, 115.98076211353315, 102.99038105676658, 72.99038105676658, 60]
        x_cop = copy.deepcopy(x)
        zmienna = 0
        k = math.sqrt(3) / 4 + 43
        for i in range(var):
            lista = []
            x = x_cop
            if i != 0:
                y = [z + k for z in y]
            if i < var / 2 and i != 0:
                x = [z - i * (math.sqrt(3) / 2 * 30) for z in x]
            if i > var / 2 and i != 0 and i != var - 1:
                x = [z - (var - 1 - i) * (math.sqrt(3) / 2 * 30) for z in x]
            for j in range(grid_size + zmienna):
                if j != 0:
                    x = [z + math.sqrt(3) / 2 * 60 for z in x]
                self.scene.addLine(x[0], y[0], x[1], y[1], blackPen)
                self.scene.addLine(x[1], y[1], x[2], y[2], blackPen)
                self.scene.addLine(x[2], y[2], x[3], y[3], blackPen)
                self.scene.addLine(x[3], y[3], x[4], y[4], blackPen)
                self.scene.addLine(x[4], y[4], x[5], y[5], blackPen)
                self.scene.addLine(x[5], y[5], x[0], y[0], blackPen)
                lista.append(Plansza(x[0], x[1], x[2], x[3], x[4], x[5], y[0], y[1], y[2], y[3], y[4], y[5], i, j))
                self.il_pol += 1
            self.pola.append(lista)

            if (i < var / 2 - 1):
                zmienna += 1
            else:
                zmienna = zmienna - 1
        return self.scene, self.pola, self.il_pol


class Stream(QObject):              # klasa do przenoszenia konsoli do qtextedit
    box = Signal(str)
    konsola = sys.stdout

    def write(self, text):
        self.konsola.write(str(text))
        self.box.emit(str(text))

    def flush(self):
        pass


# klasa tworzaca pojedynczego agenta oraz skuzaca do jego poruszania
class Field(QGraphicsItem):
    def __init__(self, pola, window, grid_size):
        super(QGraphicsItem, self).__init__()
        self.pola = pola
        self.grid_size = grid_size
        self.window = window
        self.value = 2
        self.nmb = self.rand_field()
        self.fld, self.txt = self.narysuj_klocek()

    def rand_field(self):                   # wylosowanie pozycji nowego agenta i jego wartosci (90% - wartosc:2, 10%-4)
        free = free_fields(self.pola)
        leng = len(free)
        ran = random.randint(0, leng-1)
        row, col = free[ran]
        self.pola[row][col].zajety = True

        ran2 = random.randint(0, 10)
        if ran2 == 7:
            self.value = 4

        return [row, col]

    def narysuj_klocek(self):
        n = 6
        r = 25
        s = 0
        w = 360 / n
        greenBrush = QBrush(Qt.green)
        polygon = QPolygonF()
        wsp_x = []
        wsp_y = []
        for i in range(n):  # add the points of polygon
            t = w * i + s
            x = (r + 3) * math.cos(math.radians(t) + math.radians(30))
            y = (r + 0.8) * math.sin(math.radians(t) + math.radians(30))
            x = x + self.pola[self.nmb[0]][self.nmb[1]].srodek_x
            y = y + self.pola[self.nmb[0]][self.nmb[1]].srodek_y
            wsp_x.append(x)
            wsp_y.append(y)
            polygon.append(QPointF(x, y))
        xd = QGraphicsPolygonItem(polygon)
        xd.setBrush(greenBrush)
        txt = QGraphicsTextItem(str(self.value), xd)
        txt.setPos(self.pola[self.nmb[0]][self.nmb[1]].srodek_x-6, self.pola[self.nmb[0]][self.nmb[1]].srodek_y-9)
        self.window.add_pol(xd)
        return xd, txt

    def zmien_pozycje_pg(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x) / 2
        y_mov = (self.pola[1][0].srodek_y - self.pola[0][0].srodek_y)
        czy = True
        zmienil = False

        while czy:
            czy = False
            zm = False
            if self.nmb[0] > self.grid_size - 1 and self.nmb[1] == 0 and self.pola[self.nmb[0] - 1][
                self.nmb[1]+1].zajety == False:
                zm = True
            elif self.nmb[0] > self.grid_size - 1 and self.nmb[1] != 0:
                if len(self.pola[self.nmb[0] - 1]) > self.nmb[1] + 1 and self.pola[self.nmb[0]-1][self.nmb[1]+1].zajety == False:
                    zm = True
            elif self.nmb[0] <= self.grid_size - 1 and self.nmb[0] - 1 >= 0 and len(self.pola[self.nmb[0]-1]) > self.nmb[1] and self.pola[self.nmb[0]-1][self.nmb[1]].zajety == False:
                zm = True
            if zm == True:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                if self.nmb[0] >= self.grid_size:
                    self.nmb[1] = self.nmb[1] + 1
                self.nmb[0] = self.nmb[0] - 1
                self.fld.moveBy(x_mov, -y_mov)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def zmien_pozycje_lg(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x) / 2
        y_mov = (self.pola[1][0].srodek_y - self.pola[0][0].srodek_y)
        czy = True
        zmienil = False

        while czy:
            czy = False
            zm = False
            if self.nmb[0] > self.grid_size-1 and self.nmb[1] == 0 and self.pola[self.nmb[0]-1][self.nmb[1]].zajety == False:
                zm = True
            elif self.nmb[0] > self.grid_size-1 and self.nmb[1] != 0:
                if len(self.pola[self.nmb[0] - 1]) > self.nmb[1] - 1 and self.pola[self.nmb[0]-1][self.nmb[1]].zajety == False:
                    zm = True
            if self.nmb[0] - 1 >= 0 and self.nmb[1] - 1 >= 0 and self.pola[self.nmb[0]-1][self.nmb[1]-1].zajety == False or zm == True:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                if self.nmb[0] < self.grid_size:
                    self.nmb[1] = self.nmb[1] - 1
                self.nmb[0] = self.nmb[0] - 1
                self.fld.moveBy(-x_mov, -y_mov)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def zmien_pozycje_l(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x)
        czy = True
        zmienil = False

        while czy:
            czy = False
            if self.nmb[1] - 1 >= 0 and self.pola[self.nmb[0]][self.nmb[1]-1].zajety == False:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                self.nmb[1] = self.nmb[1] - 1
                self.fld.moveBy(-x_mov, 0)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def zmien_pozycje_p(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x)
        czy = True
        zmienil = False

        while czy:
            czy = False
            if self.nmb[1] + 1 < len(self.pola[self.nmb[0]]) and self.pola[self.nmb[0]][self.nmb[1]+1].zajety == False:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                self.nmb[1] = self.nmb[1] + 1
                self.fld.moveBy(x_mov, 0)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def zmien_pozycje_ld(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x) / 2
        y_mov = (self.pola[1][0].srodek_y - self.pola[0][0].srodek_y)
        czy = True
        zmienil = False

        while czy:
            czy = False
            zm = False
            if self.nmb[0] < self.grid_size - 1 and self.nmb[1] == 0 and self.pola[self.nmb[0] + 1][
                self.nmb[1]].zajety == False:
                zm = True
            elif self.nmb[0] < self.grid_size - 1 and self.nmb[1] != 0:     #
                if self.nmb[1] - 1 >= 0 and self.pola[self.nmb[0] + 1][
                self.nmb[1]].zajety == False:                                   #
                    zm = True                                               #
            if self.nmb[0] + 1 < self.grid_size*2-1 and self.nmb[1] - 1 >= 0 and self.pola[self.nmb[0] + 1][
                self.nmb[1] - 1].zajety == False or zm == True:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                if self.nmb[0] >= self.grid_size-1:
                    self.nmb[1] = self.nmb[1] - 1
                self.nmb[0] = self.nmb[0] + 1
                self.fld.moveBy(-x_mov, y_mov)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def zmien_pozycje_pd(self):
        x_mov = (self.pola[0][1].srodek_x - self.pola[0][0].srodek_x) / 2
        y_mov = (self.pola[1][0].srodek_y - self.pola[0][0].srodek_y)
        czy = True
        zmienil = False

        while czy:
            czy = False
            zm = False
            if self.nmb[0] < self.grid_size - 1 and self.nmb[1] == 0 and self.pola[self.nmb[0] + 1][
                self.nmb[1]+1].zajety == False:
                zm = True
            elif self.nmb[0] < self.grid_size - 1 and self.nmb[1] != 0:  #
                if self.nmb[1] + 1 < len(self.pola[self.nmb[0]+1]) and self.pola[self.nmb[0]+1][self.nmb[1]+1].zajety == False:  #
                    zm = True
            elif self.nmb[0] >= self.grid_size - 1 and self.nmb[0] + 1 < self.grid_size * 2 - 1 and \
                    self.nmb[1] + 1 >= 0 and len(self.pola[self.nmb[0]+1]) > self.nmb[1] and self.pola[self.nmb[0] + 1][
                self.nmb[1]].zajety == False:
                zm = True
            if zm == True:
                self.pola[self.nmb[0]][self.nmb[1]].zajety = False
                self.window.del_pol(self.fld)
                if self.nmb[0] < self.grid_size - 1:
                    self.nmb[1] = self.nmb[1] + 1
                self.nmb[0] = self.nmb[0] + 1
                self.fld.moveBy(x_mov, y_mov)
                self.pola[self.nmb[0]][self.nmb[1]].zajety = True
                self.window.add_pol(self.fld)
                czy = True
                zmienil = True
        return zmienil

    def upd_text(self):                     # metoda aktualizujaca wartosc klocka
        self.txt.setPlainText(str(self.value))
        if self.value == 16:
            self.txt.moveBy(-4, 0)
        elif self.value == 128:
            self.txt.moveBy(-2, 0)
        return self.value


# zwraca indeksy wolnych pol
def free_fields(pola):
    free = []
    for i in range(len(pola)):
        for j in range(len(pola[i])):
            if pola[i][j].zajety == False:
                free.append([i, j])
    return free


def main():
    app = QApplication(sys.argv)
    window = Window(3)

    sys.exit(app.exec_())


main()