from main_class import *
import ctypes

myappid = u'mrmiquy.heh.hehTyper.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QApplication(sys.argv)

heh = main_class(language = 'en', text_length = 200)

sys.exit(app.exec_())