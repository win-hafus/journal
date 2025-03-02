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
