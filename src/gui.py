### DO NOT RUN IN GOOGLE COLAB

import sys, random
# !pip install PyQt5 #if needed
import PyQt5.QtWidgets
import pandas as pd 
import numpy as np
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit
)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QDateTime

def rank_suffix(rank):
  pass

class StateInfo(QWidget):
    
    # Note: This is 2019 data
    def __init__(self):
        super().__init__()

        # Next, we import our data which is retrieved from our visualize_data() method. 
        # We could call the function, but for simplicity's sake, we will just copy and paste it.
        arr = [['West Virginia',166.680,64360.0,51.6],
                ['Oklahoma',166.681,80040.0,59.7],
                ['Mississippi',168.644,81240.0,63.7],
                ['Ohio',169.279,87820.0,50.4],
                ['Indiana',170.603,75280.0,51.3],
                ['Arkansas',171.904,'Not Available*',60.4],
                ['Kansas',176.342,93070.0,54.1],
                ['Alabama',179.617,84470.0,63.1],
                ['Iowa',181.556,91470.0,47.5],
                ['Texas',181.626,114360.0,64.6],
                ['Illinois',182.404,104010.0,51.6],
                ['Michigan',182.567,86680.0,43.6],
                ['Missouri',183.027,89570.0,54.5],
                ['Kentucky',184.421,79860.0,55.5],
                ['Louisiana',184.833,79470.0,66.4],
                ['Nevada',186.893,97710.0,49.5],
                ['Georgia',187.041,104760.0,63.4],
                ['Nebraska',188.228,80590.0,48.4],
                ['Alaska',191.062,105150.0,'Not Available*'],
                ['South Carolina',192.268,100620.0,62.4],
                ['Tennessee',192.529,90720.0,57.7],
                ['North Carolina',192.695,113980.0,58.5],
                ['New Mexico',193.538,80290.0,52.8],
                ['Pennsylvania',197.418,92760.0,48.1],
                ['Connecticut',197.542,102100.0,48.1],
                ['Wisconsin',198.622,71710.0,42.3],
                ['North Dakota',204.915,94230.0,39.6],
                ['South Dakota',205.622,87560.0,44.6],
                ['Minnesota',209.745,106130.0,40.1],
                ['Arizona',212.253,96990.0,59.3],
                ['Virginia',212.256,115630.0,54.8],
                ['Idaho',212.842,99240.0,42.6],
                ['Vermont',214.132,116220.0,41.4],
                ['Wyoming',214.690,'Not Available*',40.7],
                ['Delaware',217.276,127810.0,54.2],
                ['Florida',217.577,90850.0,70.2],
                ['Maryland',217.911,117660.0,53.8],
                ['New Hampshire',220.409,96100.0,42.4],
                ['Maine',226.229,90410.0,40.1],
                ['Hawaii',228.678,84200.0,'Not Available*'],
                ['California',234.039,133110.0,57.3],
                ['Rhode Island',239.462,103950.0,48.6],
                ['New Jersey',240.594,120240.0,51.4],
                ['New York',243.357,122540.0,44.5],
                ['Washington',244.766,133900.0,46.1],
                ['Utah',245.812,79830.0,47.5],
                ['Montana',246.046,77830.0,41.2],
                ['Oregon',255.429,111240.0,46.5],
                ['Colorado',255.573,105790.0,44.6],
                ['Massachusetts',305.711,111550.0,46.9]]
        self.df = pd.DataFrame(arr, columns = ['State', 'HPI', 'DS Salary', 'Temperature'])
        self.df.set_index('State', inplace=True)
        self.df.sort_index(inplace=True)

        #set window
        self.setWindowTitle("2019 USA State Info Comparison Chart")
        self.setFixedWidth(1200)
        self.setFixedHeight(600)

        ### Vars
        self.curramt = 0

        ####################################
        #Widgets
        self.title = QLabel("Select up to 5 States to Compare!")
        self.title.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        self.title.setFont(QFont('Georgia', 24))

        self.dropdown = QComboBox()
        self.enter_button = QPushButton("Enter")
        self.update_label = QLabel("")
        self.update_label.setAlignment(Qt.AlignCenter)


        self.tempbox = QVBoxLayout()
        self.tempbox.addWidget(QLabel(" "))
        self.tempbox.addWidget(QLabel(" "))
        self.tempbox.addWidget(QLabel(" "))
        self.tempbox.addWidget(QLabel(" "))
        self.badbutton1 = QPushButton(" ")
        self.badbutton1.setEnabled(False)
        self.tempbox.addWidget(self.badbutton1)
        self.badbutton1.hide()
        self.tempbox_frame = QFrame()
        self.tempbox_frame.setLayout(self.tempbox)


        self.info_vbox = QVBoxLayout()
        self.info_vbox.addWidget(QLabel("State: "), alignment=Qt.AlignRight)
        self.info_vbox.addWidget(QLabel("Data Scientist Annual Salary: "), alignment=Qt.AlignRight)
        self.info_vbox.addWidget(QLabel("HPI (Housing Price Index): "), alignment=Qt.AlignRight)
        self.info_vbox.addWidget(QLabel("Average Annual Temperature: "), alignment=Qt.AlignRight)
        self.badbutton = QPushButton(" ")
        self.badbutton.setEnabled(False)
        self.info_vbox.addWidget(self.badbutton)


        self.info_vbox_frame = QFrame()
        self.info_vbox_frame.setLayout(self.info_vbox)
        self.info_vbox_frame.hide()

        self.spacer = QLabel(' \n ')
        self.disclaimer = QLabel("*Disclaimer: \n\
            Alaska and Hawaii do not have temperature values available.\n\
            Wyoming does not recognize 'Data Scientist' as an official occupation.\n\
            Arkansas does not release earnings estimates for Data Scientists")
        self.disclaimer.setAlignment(Qt.AlignCenter)

        self.reset = QPushButton("Reset")
        for a in list(self.df.index):
            self.dropdown.addItem(a) 
        

        self.enter_button.clicked.connect(lambda: self.add_state(self.dropdown.currentText()))
        
        ####################################
        #layout
        self.outer = QVBoxLayout()
        #level 1-
        vbox1 = QVBoxLayout()
        vbox1.addWidget(self.title)

        self.outer.addLayout(vbox1)

        #level 2-
        self.level2 = QVBoxLayout()
        self.level2sec = QHBoxLayout()

        self.level2sec.addWidget(self.dropdown)
        self.level2sec.addWidget(self.enter_button)
        self.level2.addLayout(self.level2sec)
        self.level2.addWidget(self.update_label)
        self.outer.addLayout(self.level2)

        # #level 3
        self.level3 = QHBoxLayout()

        self.level3.addWidget(self.tempbox_frame)
        self.level3.addWidget(self.info_vbox_frame)
        self.level3.setAlignment(Qt.AlignCenter)
        self.outer.addLayout(self.level3)

        #level 4
        self.level4 = QVBoxLayout()

        self.level4.addWidget(self.spacer)
        self.level4.addWidget(self.disclaimer)
        self.outer.addLayout(self.level4)


        #level 5
        self.level5 = QVBoxLayout()
        self.level5.addWidget(self.reset)
        self.reset.clicked.connect(lambda: self.remove_all())
        self.outer.addLayout(self.level5)

        self.setLayout(self.outer)

    def add_state(self, state_tup):
        if self.curramt >= 5:
            self.update_label.setText('Maximum amount of states already selected!')
            return
        if self.curramt == 0:
            self.level3.addWidget(self.info_vbox_frame)
            self.info_vbox_frame.show()

        # State 1 Info
        st_inf = self.df.loc[state_tup]
        s_vbox = QVBoxLayout()
        s_1 = QLabel(state_tup)
        s_1.setAlignment(Qt.AlignCenter)
        s_vbox.addWidget(s_1)
        s_2 = QLabel(f'{str("$" + str(st_inf[1]) + "0") if str(st_inf[1])[:-3].isdigit() else st_inf[1]}')
        s_2.setAlignment(Qt.AlignCenter)
        s_vbox.addWidget(s_2)
        s_3 = QLabel(f'{st_inf[0]}')
        s_3.setAlignment(Qt.AlignCenter)
        s_vbox.addWidget(s_3)
        s_4 = QLabel(f"{(str(st_inf[2]) + '°F  (' + str(round((float(st_inf[2]) - 30) * 5 / 9, 1)) + '°C)') if str(st_inf[2])[:-2].isdigit() else st_inf[2]}")
        s_4.setAlignment(Qt.AlignCenter)
        s_vbox.addWidget(s_4)
        button1 = QPushButton("Remove", self)
        s_vbox.addWidget(button1)


        s_frame = QFrame()
        s_frame.setLayout(s_vbox)
        self.level3.addWidget(s_frame)
        s_frame.show()

        button1.clicked.connect(lambda: self.remove_state())

        self.curramt += 1
        self.update_title()

    def remove_state(self):
        self.level3.removeWidget(self.sender().parent())
        self.curramt -= 1
        self.update_title()
        self.update_label.setText('')
        if self.curramt == 0:
            self.info_vbox_frame.hide()


    def update_title(self):
        self.title.setText(f'Select up to {5 - self.curramt} More States to Compare!')

    def remove_all(self):
        for i in reversed(range(1, self.level3.count())): 
            self.level3.itemAt(i).widget().setParent(None)
        self.curramt = 0
        self.title.setText('Select up to 5 States to Compare!')
        self.update_label.setText('')
        self.info_vbox_frame.hide()
