import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                             QFileDialog, QMessageBox, QToolBar, QSplitter,
                             QVBoxLayout, QWidget)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Editor с Консолью')
        self.setGeometry(100, 100, 900, 700)

        try:
            open_icon = QIcon('icons/open.png')
            save_icon = QIcon('icons/save.png')
            cut_icon = QIcon('icons/cut.png')
            run_icon = QIcon('icons/run.png')
        except Exception as e:
            print(f"Предупреждение: Не удалось загрузить иконки. Убедитесь, что папка 'icons' существует. {e}")
            open_icon, save_icon, cut_icon, run_icon = QIcon(), QIcon(), QIcon(), QIcon()

        open_action = QAction(open_icon, 'Открыть...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)

        save_action = QAction(save_icon, 'Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)

        cut_action = QAction(cut_icon, 'Вырезать', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut_text)

        run_action = QAction(run_icon, 'Запустить скрипт', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_script)
        
        toolbar = QToolBar('Главная')
        self.addToolBar(toolbar)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(cut_action)
        toolbar.addSeparator()
        toolbar.addAction(run_action)

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 14pt;")

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; background-color: #2b2b2b; color: #d3d3d3; font-size: 12pt;")

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.text_edit)
        splitter.addWidget(self.console_output)
        splitter.setSizes([500, 200])

        self.setCentralWidget(splitter)
        self.show()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Python Files (*.py);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read())
                    self.current_file_path = path
                    self.setWindowTitle(f'Редактор - {path}')
            except Exception as e:
                self.show_error_message("Ошибка открытия", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        if self.current_file_path is None:
            return self.save_file_as()
        else:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                return True
            except Exception as e:
                self.show_error_message("Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")
                return False

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Python Files (*.py);;All Files (*)")
        if path:
            self.current_file_path = path
            self.setWindowTitle(f'Редактор - {path}')
            return self.save_file()
        return False
        
    def cut_text(self):
        if self.text_edit.hasFocus():
            self.text_edit.cut()

    def run_script(self):
        if not self.save_file():
            self.console_output.append("<font color='orange'>Файл не сохранен. Запуск отменен.</font><br>")
            return
        
        self.console_output.clear()
        self.console_output.append(f"<font color='gray'>Запуск {self.current_file_path}...</font><br>")
        
        process = subprocess.Popen(['python', '-u', self.current_file_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   encoding='utf-8',
                                   bufsize=1)

        for line in iter(process.stdout.readline, ''):
            self.console_output.append(line.strip())
        
        process.wait()
        stderr_output = process.stderr.read()

        if stderr_output:
            self.console_output.append(f"<font color='red'>{stderr_output.strip()}</font>")
        
        self.console_output.append(f"<br><font color='gray'>--- Выполнение завершено с кодом {process.returncode} ---</font>")

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CodeEditor()
    sys.exit(app.exec_())