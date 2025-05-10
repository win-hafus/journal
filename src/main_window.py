from PyQt5.QtWidgets import QMainWindow, QTabWidget
from .data_manager import DataManager
from .homework_tab import HomeworkTab
from .schedule_tab import ScheduleTab
from .subjects_tab import SubjectsTab
from .grades_tab import GradesTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Школьный дневник')
        self.setGeometry(100, 100, 800, 600)
        
        self.data_manager = DataManager()
        self.tabs = QTabWidget()
        
        self._init_tabs()
        self._connect_signals()
        self._apply_styles()
        self.setCentralWidget(self.tabs)

    def _init_tabs(self):
        self.tabs.addTab(ScheduleTab(self.data_manager), 'Расписание')
        self.tabs.addTab(HomeworkTab(self.data_manager), 'Домашние задания')
        self.tabs.addTab(SubjectsTab(self.data_manager), 'Предметы')
        self.tabs.addTab(GradesTab(self.data_manager), 'Оценки')

    def _connect_signals(self):
        self.data_manager.subjects_updated.connect(self.tabs.widget(0).refresh_data)
        self.data_manager.schedule_updated.connect(self.tabs.widget(0).refresh_data)
        self.data_manager.homework_updated.connect(self.tabs.widget(1).refresh_data)
        self.data_manager.subjects_updated.connect(self.tabs.widget(2).refresh_data)
        self.data_manager.grades_updated.connect(self.tabs.widget(3).refresh_data)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: #fff;
                margin: 0px;
                padding: 5px 0;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom-color: #ccc;
                padding: 10px 20px;
                font-size: 12px;
                color: #333;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            
            QTabBar::tab:selected {
                background-color: #fff;
                border-bottom-color: #fff;
                color: #000;
            }
            
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            
            QTabBar::close-button {
                subcontrol-position: right;
                padding: 2px;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)
