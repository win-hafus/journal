from PyQt5.QtWidgets import QMainWindow, QTabWidget
from src.schedule_tab import ScheduleTab
from src.homework_tab import HomeworkTab
from src.subjects_tab import SubjectsTab
from src.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Школьный дневник')
        self.setGeometry(100, 100, 800, 600)
        
        self.data_manager = DataManager()
        
        self.tabs = QTabWidget()
        self.tabs.addTab(ScheduleTab(self.data_manager), 'Расписание')
        self.tabs.addTab(HomeworkTab(self.data_manager), 'Домашние задания')
        self.tabs.addTab(SubjectsTab(self.data_manager), 'Предметы')
        
        self.setCentralWidget(self.tabs)

        self.setStyleSheet("""
            /* Стилизация главного окна */
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            /* Стилизация QTabWidget */
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: #fff;
                margin: 0px;
                padding: 0px;
            }
            
            /* Стилизация вкладок */
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
            
            /* Стилизация активной вкладки */
            QTabBar::tab:selected {
                background-color: #fff;
                border-bottom-color: #fff;
                color: #000;
            }
            
            /* Стилизация при наведении на вкладку */
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            
            /* Стилизация кнопок закрытия вкладок (если они есть) */
            QTabBar::close-button {
                subcontrol-position: right;
                padding: 2px;
            }
            
            /* Стилизация области содержимого вкладок */
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)
