from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from src.data_manager import DAYS_OF_WEEK, MAX_LESSONS

class ScheduleTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.schedule = self.data_manager.load_schedule()
        self.subjects = self.data_manager.load_subjects()
        self.current_date = QDate.currentDate()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Панель навигации
        nav_layout = QHBoxLayout()
        self.prev_week_btn = QPushButton('← Предыдущая')
        self.prev_week_btn.clicked.connect(self.prev_week)
        self.next_week_btn = QPushButton('Следующая →')
        self.next_week_btn.clicked.connect(self.next_week)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.current_date)
        self.date_edit.dateChanged.connect(self.date_changed)
        
        nav_layout.addWidget(self.prev_week_btn)
        nav_layout.addWidget(QLabel("Неделя:"))
        nav_layout.addWidget(self.date_edit)
        nav_layout.addWidget(self.next_week_btn)
        
        # Настройка таблицы
        self.table = QTableWidget(MAX_LESSONS, len(DAYS_OF_WEEK))
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Настройка шрифтов
        self.table_font = QFont()
        self.table_font.setPointSize(12)
        
        # Настройка заголовков
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.horizontalHeader().setDefaultSectionSize(180)
        self.table.horizontalHeader().setMinimumSectionSize(100)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Стилизация
        self.setStyleSheet("""
            /* Стилизация кнопок переключения недели */
            QPushButton {
                font-size: 12pt;
                padding: 8px 16px;
                margin-top: 5px;
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

            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                padding: 10px;
                qproperty-alignment: AlignCenter;  /* Центрируем текст */
            }
            
            /* Стилизация QTableWidget (таблица) */
            QTableWidget {
                font-size: 12pt;
                background-color: #f9f9f9;
                gridline-color: #ddd;
            }
            
            QHeaderView::section {
                font-size: 12pt;
                padding: 10px;
                border: 1px solid #ddd;
                background-color: #e0e0e0;
            }
            
            QTableWidget::item {
                border: 1px solid #ddd;
            }
            
            QTableWidget::item:selected {
                background-color: #cce8ff;
                color: #000;
            }
            
            QComboBox {
                font-size: 12pt;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            
            QComboBox::down-arrow {
                image: url(down_arrow.png);  /* Замените на путь к вашему изображению */
            }
            
            QComboBox QAbstractItemView {
                font-size: 12pt;
                padding: 10px;
                border: 1px solid #ccc;
                background-color: #fff;
                selection-background-color: #cce8ff;
            }
        """)        
        layout.addLayout(nav_layout)
        layout.addWidget(self.table, 1)
        
        self.setLayout(layout)
        self.update_headers()
        self.update_table()
        
    def get_current_week_start(self):
        return self.current_date.addDays(-(self.current_date.dayOfWeek() - 1))
    
    def get_week_dates(self):
        start_date = self.get_current_week_start()
        return [start_date.addDays(i) for i in range(6)]
    
    def update_headers(self):
        dates = self.get_week_dates()
        headers = []
        for date, day in zip(dates, DAYS_OF_WEEK):
            headers.append(f"{day}\n{date.toString('dd.MM.yyyy')}")
        self.table.setHorizontalHeaderLabels(headers)
        
    def get_schedule_for_date(self, target_date):
        target_date_str = target_date.toString("yyyy-MM-dd")
        schedule = {}
        
        for day in DAYS_OF_WEEK:
            day_schedule = self.schedule.get(day, [])
            latest_subjects = [''] * MAX_LESSONS
            
            for version in sorted(day_schedule, 
                               key=lambda x: x['start_date'], 
                               reverse=True):
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
    
    def update_table(self):
        self.table.blockSignals(True)
        self.table.clearContents()
        
        # Обновляем список предметов
        self.subjects = self.data_manager.load_subjects()
        
        for col in range(len(DAYS_OF_WEEK)):
            current_date = self.get_current_week_start().addDays(col)
            schedule = self.get_schedule_for_date(current_date)
            day = DAYS_OF_WEEK[col]
            subjects = schedule.get(day, [''] * MAX_LESSONS)
            
            for row in range(MAX_LESSONS):
                combo = QComboBox()
                combo.addItem("")  # Пустой элемент
                combo.addItems(self.subjects)
                
                # Устанавливаем текущее значение
                current_value = subjects[row] if row < len(subjects) else ''
                index = combo.findText(current_value)
                combo.setCurrentIndex(index if index != -1 else 0)
                
                # Подключаем сигнал изменения
                combo.currentTextChanged.connect(
                    lambda text, r=row, c=col: self.on_subject_changed(text, r, c)
                )
                
                self.table.setCellWidget(row, col, combo)
        
        self.table.blockSignals(False)
        
    def on_subject_changed(self, text, row, col):
        day_of_week = DAYS_OF_WEEK[col]
        week_start = self.get_current_week_start().toString("yyyy-MM-dd")
        
        day_schedule = self.schedule.setdefault(day_of_week, [])
        current_version = next(
            (v for v in day_schedule if v['start_date'] == week_start),
            None
        )
        
        if not current_version:
            prev_subjects = self.get_schedule_for_date(
                self.get_current_week_start().addDays(-1)
            )[day_of_week]
            
            current_version = {
                'start_date': week_start,
                'subjects': prev_subjects.copy()
            }
            day_schedule.append(current_version)
        
        if len(current_version['subjects']) <= row:
            current_version['subjects'] += [''] * (row - len(current_version['subjects']) + 1)
        current_version['subjects'][row] = text
        
        self.data_manager.save_schedule(self.schedule)
        
    def prev_week(self):
        self.current_date = self.current_date.addDays(-7)
        self.date_edit.setDate(self.current_date)
        self.update_headers()
        self.update_table()
        
    def next_week(self):
        self.current_date = self.current_date.addDays(7)
        self.date_edit.setDate(self.current_date)
        self.update_headers()
        self.update_table()
        
    def date_changed(self, date):
        self.current_date = date
        self.update_headers()
        self.update_table()
