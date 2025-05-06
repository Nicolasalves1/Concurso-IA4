import sys
from PyQt5.QtWidgets import QApplication
from interface import CompatibilidadeApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = CompatibilidadeApp()
    janela.show()
    sys.exit(app.exec_())
    