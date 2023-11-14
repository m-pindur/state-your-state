import gui

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = StateInfo()
    # with open("guistyle.css") as fin:
    #     app.setStyleSheet(fin.read())
    main.show()
    exit_code = app.exec_()
    sys.exit(exit_code)
