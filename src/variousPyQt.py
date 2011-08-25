import sys
from qt import *

class HelloButton(QPushButton):

    def __init__(self, *args):
        apply(QPushButton.__init__, (self,) + args)
        self.setText("Hello World")

class HelloWindow(QMainWindow):

    def __init__(self, *args):
        apply(QMainWindow.__init__, (self,) + args)
        self.button=HelloButton(self)
        self.setCentralWidget(self.button)

def main(args):
    app=QApplication(args)
    win=HelloWindow()
    win.show()
    app.connect(app, SIGNAL("lastWindowClosed()"),
                app, SLOT("quit()"))
    app.exec_loop()

if __name__=="__main__":
    main(sys.argv)
