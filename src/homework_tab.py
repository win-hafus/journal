from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from src.data_manager import DAYS_OF_WEEK, MAX_LESSONS

class HomeworkTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.homework = self.data_manager.load_homework()
        self.current_date = QDate.currentDate()
        self.current_subject = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        
        nav_layout = QHBoxLayout()
        self.prev_day_btn = QPushButton('← Предыдущий')
        self.prev_day_btn.clicked.connect(self.prev_day)
        self.next_day_btn = QPushButton('Следующий →')
        self.next_day_btn.clicked.connect(self.next_day)
        self.date_label = QLabel(self.current_date.toString())
        
        nav_layout.addWidget(self.prev_day_btn)
        nav_layout.addWidget(self.date_label)
        nav_layout.addWidget(self.next_day_btn)
        
        self.schedule_table = QTableWidget(MAX_LESSONS, 1)
        self.schedule_table.setHorizontalHeaderLabels(["Предметы"])
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setSelectionMode(QTableWidget.SingleSelection)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.cellClicked.connect(self.on_subject_selected)
        
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.verticalHeader().setDefaultSectionSize(40)
        
        left_panel.addLayout(nav_layout)
        left_panel.addWidget(self.schedule_table)
        
        self.homework_edit = QTextEdit()
        self.homework_edit.setPlaceholderText("Выберите предмет для добавления домашнего задания")
        self.homework_edit.textChanged.connect(self.save_homework)
        
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.homework_edit, 2)
        
        self.setLayout(main_layout)
        self.update_schedule()
        
        # Применение стилей
        self.setStyleSheet("""
            /* Стилизация QTableWidget (таблица предметов) */
            QTableWidget {
                font-size: 14px;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                gridline-color: #ddd;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            
            QTableWidget::item:selected {
                background-color: #cce8ff;
                color: #000;
            }
            
            QHeaderView::section {
                font-size: 14px;
                padding: 10px;
                background-color: #e0e0e0;
                border: 1px solid #ccc;
            }
            
            /* Стилизация QPushButton (кнопки) */
            QPushButton {
                font-size: 14px;
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f0f0f0;
                color: #333;
            }
            
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            
            /* Стилизация QTextEdit (поле для домашнего задания) */
            QTextEdit {
                font-size: 14px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            
            QTextEdit:focus {
                border-color: #66afe9;
            }
            
            /* Стилизация QLabel (метка даты) */
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
        """)
        
    def update_schedule(self):
        self.schedule_table.blockSignals(True)
    
        # Получаем индекс дня недели (0-6)
        day_of_week_index = self.current_date.dayOfWeek() - 1
    
        # Проверяем, что индекс в пределах списка DAYS_OF_WEEK
        if day_of_week_index < len(DAYS_OF_WEEK):
            day_of_week = DAYS_OF_WEEK[day_of_week_index]
            schedule = self.get_schedule_for_date(self.current_date)
            subjects = schedule.get(day_of_week, [''] * MAX_LESSONS)
        
            # Заполняем таблицу
            self.schedule_table.setRowCount(MAX_LESSONS)
            for row in range(MAX_LESSONS):
                item = QTableWidgetItem(subjects[row] if row < len(subjects) else '')
                item.setTextAlignment(Qt.AlignCenter)
                self.schedule_table.setItem(row, 0, item)
    
        self.schedule_table.blockSignals(False)
        self.date_label.setText(self.current_date.toString("dd.MM.yyyy"))
            
    def get_schedule_for_date(self, target_date):
        target_date_str = target_date.toString("yyyy-MM-dd")
        schedule = {}
        
        for day in DAYS_OF_WEEK:
            day_schedule = self.data_manager.load_schedule().get(day, [])
            latest_subjects = [''] * MAX_LESSONS
            
            for version in sorted(day_schedule, key=lambda x: x['start_date'], reverse=True):
                if version['start_date'] <= target_date_str:
                    subjects = version.get('subjects', [])
                    if isinstance(subjects, list):
                        latest_subjects = [
                            str(subj).strip() 
                            for subj in subjects[:MAX_LESSONS]
                        ] + [''] * (MAX_LESSONS - len(subjects))
                    break
                    
            schedule[day] = latest_subjects
        
        return schedule
        
    def on_subject_selected(self, row, col):
        item = self.schedule_table.item(row, 0)
        if item:
            self.current_subject = item.text()
            self.load_homework()
        
    def load_homework(self):
        if self.current_subject:
            date_str = self.current_date.toString("yyyy-MM-dd")
            hw_data = self.homework.get(date_str, {})
            self.homework_edit.setPlainText(hw_data.get(self.current_subject, ""))
            self.homework_edit.setEnabled(True)
        else:
            self.homework_edit.clear()
            self.homework_edit.setEnabled(False)
            
    def save_homework(self):
        if self.current_subject:
            date_str = self.current_date.toString("yyyy-MM-dd")
            text = self.homework_edit.toPlainText()
            if date_str not in self.homework:
                self.homework[date_str] = {}
            self.homework[date_str][self.current_subject] = text
            self.data_manager.save_homework(self.homework)
            
    def prev_day(self):
        self.current_date = self.current_date.addDays(-1)
        self.update_schedule()
        self.clear_selection()
        
    def next_day(self):
        self.current_date = self.current_date.addDays(1)
        self.update_schedule()
        self.clear_selection()
        
    def clear_selection(self):
        self.schedule_table.clearSelection()
        self.current_subject = None
        self.homework_edit.clear()
        self.homework_edit.setEnabled(False)
