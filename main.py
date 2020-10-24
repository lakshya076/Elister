from PySide2.QtCore import SIGNAL, QSize, Qt, QUrl
from PySide2.QtWidgets import QLineEdit, QMainWindow, QTabWidget, QAction, QToolBar, QStatusBar, QLabel, QFileDialog, \
    QApplication, QDialog, QDialogButtonBox, QVBoxLayout
from PySide2.QtGui import QPalette, QPixmap, QColor, QIcon, QCursor, QKeySequence
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtPrintSupport import QPrintPreviewDialog
import os
import sys


class LineEdit(QLineEdit):
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)

    def mousePressEvent(self, QMouseEvent):
        self.emit(SIGNAL("clicked()"))


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setWindowIcon(QPixmap(os.path.join('images', 'logo.PNG')))

        layout = QVBoxLayout()

        title = QLabel("Elister")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'logo.PNG')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 1.0.0"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class Browser(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)

        self.setGeometry(30, 40, 1000, 500)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.palette = QPalette()
        self.palette.setColor(self.palette.Window, QColor('#454545'))
        self.palette.setColor(self.palette.WindowText, QColor('#034343'))
        self.setPalette(self.palette)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        back_btn = QAction(QIcon(os.path.join('images', 'arrow-180.png')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(os.path.join('images', 'arrow-000.png')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(QIcon(os.path.join('images', 'arrow-circle-315.png')), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join('images', 'home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()  # Yes, really!
        self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))
        navtb.addWidget(self.httpsicon)

        self.urlbar = LineEdit(parent=None)
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.urlbar.setCursor(QCursor(Qt.IBeamCursor))
        self.urlbar.setFixedHeight(30)
        self.connect(self.urlbar, SIGNAL("clicked()"), self.select)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon(os.path.join('images', 'cross-circle.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction(QIcon(os.path.join('images', 'ui-tab--plus.png')), "New Tab", self)
        new_tab_action.setStatusTip("Open a new tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        new_tab_action.setShortcut(QKeySequence('Ctrl+N'))
        file_menu.addAction(new_tab_action)

        open_file_action = QAction(QIcon(os.path.join('images', 'disk--arrow.png')), "Open file...", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        open_file_action.setShortcut(QKeySequence('Ctrl+O'))
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save Page As...", self)
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        save_file_action.setShortcut(QKeySequence('Ctrl+S'))
        file_menu.addAction(save_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        print_action.setShortcut(QKeySequence('Ctrl+P'))
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join('images', 'question.png')), "About Elister", self)
        about_action.setStatusTip("Find out more about Elister")
        about_action.triggered.connect(self.about)
        about_action.setShortcut(QKeySequence('Alt+A'))
        help_menu.addAction(about_action)

        navigate_elister_action = QAction(QIcon(os.path.join('images', 'lifebuoy.png')), "Elister Homepage", self)
        navigate_elister_action.setStatusTip("Go to Elister Homepage")
        navigate_elister_action.triggered.connect(self.navigate_elister)
        navigate_elister_action.setShortcut(QKeySequence('Ctrl+H'))
        help_menu.addAction(navigate_elister_action)

        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')

        self.show()

        self.setWindowTitle("Elister")
        self.setWindowIcon(QIcon(os.path.join('images', 'ma-icon-64.png')))

    def select(self):
        self.urlbar.selectAll()

    def add_new_tab(self, qurl=None, label="Blank"):

        browser = QWebEngineView()
        browser.setUrl("https://www.google.com/")
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f'{title} - Elister')

    def navigate_elister(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")

        if filename:
            html = self.tabs.currentWidget().page().toHtml()
            with open(filename, 'w') as f:
                f.write(html.encode('utf8'))

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        last = self.urlbar.text()[-1:]

        if f'{str(self.urlbar.text())[-4:-1]}{last}' == '.com':
            try:
                self.tabs.currentWidget().setUrl(f'https://www.{self.urlbar.text()}')

            except Exception:
                self.tabs.currentWidget().setUrl(f'http://www.{self.urlbar.text()}')

        else:
            self.tabs.currentWidget().setUrl(f'https://www.google.com/search?q={self.urlbar.text()}')

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-ssl.png')))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Elister")
    app.setOrganizationName("Elister")

    window = Browser()
    window.show()
    sys.exit(app.exec_())
