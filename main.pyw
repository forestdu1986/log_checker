from PyQt4.QtGui import *
from PyQt4.QtCore import *
import time
import sys
from os.path import isfile

logfilename = "test.log"
def print_line(text):
    print("this is: "+text)
    
class form(QDialog):
    def __init__(self, parent = None):
        super(form, self).__init__(parent)
        
        self.pb_write = QPushButton("write log")
        self.pb_stopwrite = QPushButton("stop write")
        self.pb_stopwrite.setVisible(False)
        self.pb_follow = QPushButton("follow log")
        self.pb_getlist = QPushButton("get identifier list")
        self.pb_getfile = QPushButton("Select file")
        self.le_filepath = QLineEdit()
        self.le_filepath.setText(r"C:\Jlearn\log_checker\testlog.log")
        self.le_filepath.setFocus()
        self.le_filepath.selectAll()
        self.le_listpath = QLineEdit()
        self.le_listpath.setText(r"C:\Jlearn\log_checker\ID_list.txt")
        grdlayout = QGridLayout()
        grdlayout.addWidget(self.le_filepath, 0, 0)
        grdlayout.addWidget(self.pb_follow, 0, 1)
        grdlayout.addWidget(self.pb_write, 1, 0)
        grdlayout.addWidget(self.pb_stopwrite, 1, 0)
        grdlayout.addWidget(self.pb_getfile, 1, 1)
        grdlayout.addWidget(self.le_listpath, 2, 0)
        grdlayout.addWidget(self.pb_getlist, 2, 1)
        
        self.lb_listtitle = QLabel("list of identifier")
        self.lb_listtitle.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.ls_list = QListWidget()
        vlayout = QVBoxLayout()
        vlayout.addWidget(self.lb_listtitle)
        vlayout.addWidget(self.ls_list)
        
        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayout)
        hlayout.addLayout(grdlayout)
        
        self.setLayout(hlayout)
        
        self.pb_getlist.clicked.connect(self.getlist)
        self.pb_write.clicked.connect(self.writelog)
        self.pb_follow.clicked.connect(self.followlog)
        self.pb_stopwrite.clicked.connect(self.stopwrite)
        self.pb_getfile.clicked.connect(self.getfile)
        
        self.idlist = []
        
        self.mywriter = Writer()
        
        self.filepath = ""
        
    def getlist(self):
        filepath = self.le_listpath.text()
        if isfile(filepath):
            with open(filepath) as f:
                stripedlist = [x.strip() for x in f.readlines()]
                for line in (set(stripedlist+self.idlist) - set(self.idlist)):
                    self.ls_list.addItem(line)
                    self.idlist.append(line)
                    
        else:
            QMessageBox.information(self, "Invalid filepath", "'%s' is not a valid filepath"%filepath)
    
    def writelog(self):
        filepath = self.le_filepath.text()
        if isfile(filepath):
            self.mywriter.setfp(filepath)
            self.mywriter.start()
            self.pb_write.setVisible(False)
            self.pb_stopwrite.setVisible(True)
        else:
            QMessageBox.information(self, "Invalid filepath", "'%s' is not a valid filepath"%filepath)
    
    def stopwrite(self):
        self.mywriter.stopwrite()
        self.pb_stopwrite.setVisible(False)
        self.pb_write.setVisible(True)
            
    def followlog(self):
        filepath = self.le_filepath.text()
        if isfile(filepath):
            self.mythread = Tracker(filepath, self.idlist)
            self.connect(self.mythread, SIGNAL("output"), self.threadcallback)
            self.connect(self.mythread, SIGNAL("output1"), self.threadcallback1)
            self.mythread.start()

        else:
            QMessageBox.information(self, "Invalid filepath", "'%s' is not a valid filepath"%filepath)   

    def getfile(self):
        self.filepath = QFileDialog.getOpenFileName\
        (caption='browse file', directory=r'C:\Jlearn\log_checker', filter='Text files (*.txt *.log)')
        
                                
    def threadcallback(self, id, text):
        """match identifier, pop up message"""
        funcName = sys._getframe().f_code.co_name #获取调用函数名
        lineNumber = sys._getframe().f_back.f_lineno     #获取行号
        print(">function: %s; line: %d"%(funcName, lineNumber))
        self.lb_listtitle.setText(text)
        QMessageBox.information(self, "Found!", "new line '%s' contains '%s'"%(text, id))
        print("<function: %s; line: %d"%(funcName, lineNumber))
        
    def threadcallback1(self,text):
        """no match, update text box"""
        funcName = sys._getframe().f_code.co_name #获取调用函数名
        lineNumber = sys._getframe().f_back.f_lineno     #获取行号
        print(">function: %s; line: %d"%(funcName, lineNumber))        
        self.lb_listtitle.setText(text)   
        print("<function: %s; line: %d"%(funcName, lineNumber))
        
class Writer(QThread): 
    def __init__(self, parent = None): 
        super(Writer,self).__init__(parent) 
        self.stop = False
    
    def setfp(self, fp): 
        self.filepath = fp
        
    def stopwrite(self):
        self.stop = True

    def __del__(self): 
        self.wait() 
        
    def run(self): 
        i = 0
        self.stop = False
        while not self.stop:
            with open(self.filepath, "a+") as f:
                f.write("test1 %d value #%d#\n"%(i, i%10))
                i = i+1
            time.sleep(1)

class Tracker(QThread): 
    def __init__(self, fp, idlst, parent = None): 
        super(Tracker,self).__init__(parent) 
        self.filepath = fp
        self.idlist = idlst

    def __del__(self): 
        self.wait() 
        
    def run(self): 
        with open(self.filepath) as file_:
            #read and discard the lines that's already existing
            file_.readlines()
            #start the reading loop
            while True:
                lines = file_.readlines()
                if not lines:
                    print("no new line")
                else:
                    for line in lines:
                        #print(line)
                        self.matched(line)
                time.sleep(1)
         
    def matched(self, text):
        funcName = sys._getframe().f_code.co_name #获取调用函数名
        lineNumber = sys._getframe().f_back.f_lineno     #获取行号
        print(">function: %s; line: %d"%(funcName, lineNumber))           
        self.emit(SIGNAL('output1'), text)
        for myid in self.idlist:
            if myid in text:
                self.emit(SIGNAL('output'),myid, text)
        print("<function: %s; line: %d"%(funcName, lineNumber))
                
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = form()
    Form.show()
    app.exec_()
    
#     T = Tail(logfilename)
#     T.register_callback(print_line)
#     T.follow()
#     


