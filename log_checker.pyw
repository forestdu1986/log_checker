from PyQt4.QtGui import *
from PyQt4.QtCore import *
import time
import sys
from os.path import isfile

class form(QDialog):
    """main window containing all widget"""
    def __init__(self, parent = None):
        super(form, self).__init__(parent)
        
        self.setWindowTitle("Log Monitor")
        #text box serve as main monitor of the target file
        self.te_main = QTextEdit()
        self.te_main.setReadOnly(True)
        
        #target file browser to select and display the target file path
        self.pb_target = QPushButton("Target file")
        self.lb_target = QLabel("Please select target file")
        self.lb_target.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        
        #identifier file browser to select and display the identifier file path
        self.pb_id = QPushButton("Identifier file")
        self.lb_id = QLabel("Please select the identifier file")
        self.lb_id.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        
        #Start/stop monitor
        self.pb_mntstart = QPushButton("Start Monitor")
        self.pb_mntstart.setVisible(False)
        self.pb_mntstop = QPushButton("stop Monitor")
        self.pb_mntstop.setVisible(False)
        
        #Start/stop writer
        self.pb_wstart = QPushButton("Start Writer")
        self.pb_wstart.setVisible(False)
        self.pb_wstop = QPushButton("Stop Writer")
        self.pb_wstop.setVisible(False)
        
        #list to display the identifiers
        self.list_id = QListWidget()
        
        #setup layout
        glayout = QGridLayout()
        glayout.addWidget(self.pb_target, 0, 0)
        glayout.addWidget(self.lb_target, 0, 1)
        glayout.addWidget(self.pb_id, 1, 0)
        glayout.addWidget(self.lb_id, 1, 1)
        glayout.addWidget(self.pb_mntstart, 2, 1)
        glayout.addWidget(self.pb_mntstop, 2, 1)
        glayout.addWidget(self.pb_wstart, 2, 0)
        glayout.addWidget(self.pb_wstop, 2, 0)
        
        vlayout = QVBoxLayout()
        vlayout.addLayout(glayout)
        vlayout.addWidget(self.list_id)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.te_main)
        hlayout.addLayout(vlayout)
        
        self.setLayout(hlayout)
        
        #target filepath
        self.targetpath = ""
        
        #list that contains all the identifiers
        self.idlist = []
        
        #separate thread for monitor and writer class 
        self.monitor = Monitor()
        self.writer = Writer()
        
        #connect buttons:
        self.pb_target.clicked.connect(self.loadTarget)
        self.pb_id.clicked.connect(self.loadId)
        self.pb_mntstart.clicked.connect(self.startMonitor)
        self.pb_mntstop.clicked.connect(self.stopMonitor)
        self.pb_wstart.clicked.connect(self.startWriter)
        self.pb_wstop.clicked.connect(self.stopWriter)
        
        #connect callback to thread's signal
        self.connect(self.monitor, SIGNAL("line"), self.monitorCallback)
    
    def loadTarget(self):
        """user to select the target file from file browser"""
        self.targetpath = QFileDialog.getOpenFileName\
        (caption='Please select the target file', filter='Text files (*.txt *.log)')
        if self.targetpath:
            self.lb_target.setText(self.targetpath)
            self.pb_mntstart.setVisible(True)
            self.pb_wstart.setVisible(True)
    
    def loadId(self):
        """user to select the file that contains the identifiers"""
        idpath = QFileDialog.getOpenFileName\
        (caption='Please select the id file', filter='Text files (*.txt *.log)')
        if idpath:
            self.lb_id.setText(idpath)
            self.list_id.clear()
            self.idlist = []
            with open(idpath) as f:
                #strip the lines to remove empty chars
                stripedlist = [x.strip() for x in f.readlines()]
                for line in stripedlist:
                    self.list_id.addItem(line)
                    self.idlist.append(line)
                
    def startMonitor(self):
        """Start the monitor thread to monitor identifier in log file"""
        self.monitor.setfilepath(self.targetpath)
        self.monitor.running = True
        self.monitor.start()
        self.pb_mntstart.setVisible(False)
        self.pb_mntstop.setVisible(True)
    
    def stopMonitor(self):
        """Stop the monitor thread"""
        self.monitor.running = False
        self.pb_mntstart.setVisible(True)
        self.pb_mntstop.setVisible(False)
        
        
    def monitorCallback(self, line):
        """Monitor thread callback to process the line signal"""
        self.te_main.append(line)
        for myid in self.idlist:
            if myid in line:
                QMessageBox.warning(self, "Found!", "new line '%s' contains '%s'"%(line, myid))
                
    def startWriter(self):
        """Start the writer thread to write test input to the log"""
        self.writer.setfp(self.targetpath)
        self.writer.running = True
        self.writer.start()
        self.pb_wstart.setVisible(False)
        self.pb_wstop.setVisible(True)
        
    def stopWriter(self):
        """Stop the writer thread"""
        self.writer.running = False
        self.pb_wstop.setVisible(False)
        self.pb_wstart.setVisible(True)

class Monitor(QThread):
    """separate thread class to monitor the target file's new input
    if fount new input, raise signal with new input lines"""
    def __init__(self, parent = None): 
        super(Monitor,self).__init__(parent) 
        self.filepath = ""
        self.running = False

    def __del__(self): 
        self.wait() 
        
    def run(self): 
        with open(self.filepath) as file_:
            #read and discard the lines that's already existing
            file_.readlines()
            #start the reading loop
            while self.running:
                lines = file_.readlines()
                if not lines:
                    line = "no new line"
                    self.sendline(line)
                else:
                    for line in lines:
                        self.sendline(line)
                time.sleep(1)    
    
    def sendline(self, line):
        self.emit(SIGNAL("line"), line)
        
    def setfilepath(self, fp):
        self.filepath = fp
            
class Writer(QThread):
    """Separate thread to write test input the the log file"""
    def __init__(self, parent = None): 
        super(Writer,self).__init__(parent) 
        self.running = False
    
    def setfp(self, fp): 
        self.filepath = fp
        

    def __del__(self): 
        self.wait() 
        
    def run(self): 
        i = 0
        while self.running:
            with open(self.filepath, "a+") as f:
                f.write("test1 %d value #%d#\n"%(i, i%10))
                i = i+1
            time.sleep(1)        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Form = form()
    Form.show()
    app.exec_()