from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QHeaderView, QVBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QStackedWidget, QTextBrowser, 
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTimer, QItemSelectionModel
from PyQt5.QtGui import QIcon
import markdown
from .data_manager import DataManager, DAYS_OF_WEEK, MAX_LESSONS

class HomeworkTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.homework = self.data_manager.load_homework()
        self.current_date = QDate.currentDate()
        self.current_subject = None
        self.edit_mode = False
        self.unsaved_changes = False
        self.edit_started = False
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        
        # Левая панель: навигация и таблица
        left_panel = QVBoxLayout()
        nav_layout = QHBoxLayout()
        
        self.prev_day_btn = QPushButton('← Предыдущий')
        self.next_day_btn = QPushButton('Следующий →')
        self.date_label = QLabel(self.current_date.toString("dd.MM.yyyy"))
        
        self.prev_day_btn.clicked.connect(self.prev_day)
        self.next_day_btn.clicked.connect(self.next_day)
        
        nav_layout.addWidget(self.prev_day_btn)
        nav_layout.addWidget(self.date_label)
        nav_layout.addWidget(self.next_day_btn)
        
        self.day_of_week_label = QLabel()
        self.day_of_week_label.setAlignment(Qt.AlignCenter)
        self.day_of_week_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        
        self.schedule_table = QTableWidget(MAX_LESSONS, 1)
        self.schedule_table.setHorizontalHeaderLabels(["Предметы"])
        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setSelectionMode(QTableWidget.SingleSelection)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.cellClicked.connect(self.on_subject_selected)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.verticalHeader().setDefaultSectionSize(40)
        
        left_panel.addLayout(nav_layout)
        left_panel.addWidget(self.day_of_week_label)
        left_panel.addWidget(self.schedule_table)
        
        # Правая панель: редактирование и просмотр
        right_panel = QVBoxLayout()
        
        self.toggle_edit_btn = QPushButton("Редактировать")
        self.save_btn = QPushButton("Сохранить")
        self.toggle_edit_btn.clicked.connect(self.toggle_edit_mode)
        self.save_btn.clicked.connect(self.save_homework)
        self.toggle_edit_btn.setEnabled(False)
        self.save_btn.setVisible(False)
        
        self.preview_browser = QTextBrowser()
        self.homework_edit = QTextEdit()
        self.homework_edit.textChanged.connect(self.mark_unsaved_changes)
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.preview_browser)
        self.stack.addWidget(self.homework_edit)
        
        right_panel.addWidget(self.toggle_edit_btn)
        right_panel.addWidget(self.save_btn)
        right_panel.addWidget(self.stack)
        
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        self.setLayout(main_layout)
        self.update_schedule()
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet("""
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
            
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
        """)

    def toggle_edit_mode(self):
        if not self.current_subject: 
            return
            
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.stack.setCurrentWidget(self.homework_edit)
            self.toggle_edit_btn.setText("Отменить")
            self.save_btn.setVisible(True)
            self.edit_started = True
        else:
            self.stack.setCurrentWidget(self.preview_browser)
            self.toggle_edit_btn.setText("Редактировать")
            self.save_btn.setVisible(False)
            self.edit_started = False
            self.update_preview()

    def save_homework(self):
        if self.current_subject and self.unsaved_changes:
            date_str = self.current_date.toString("yyyy-MM-dd")
            text = self.homework_edit.toPlainText()
            self.homework.setdefault(date_str, {})[self.current_subject] = text
            self.data_manager.save_homework(self.homework)
            self.unsaved_changes = False
            self.edit_started = False
            self.update_preview()

    def update_preview(self):
        html = markdown.markdown(self.homework_edit.toPlainText())
        self.preview_browser.setHtml(html)

    def check_unsaved_changes(self):
        if self.edit_started and self.unsaved_changes:
            reply = QMessageBox.question(
                self, 
                'Несохраненные изменения', 
                'Сохранить изменения перед выходом?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                self.save_homework()
                return True
            elif reply == QMessageBox.Discard:
                self.unsaved_changes = False
                self.edit_started = False
                return True
            else:
                return False
        return True

    def on_subject_selected(self, row, col):
        if not self.check_unsaved_changes(): 
            return
            
        item = self.schedule_table.item(row, 0)
        if item and item.text():
            self.current_subject = item.text()
            self.toggle_edit_btn.setEnabled(True)
            self.load_homework()

    def load_homework(self):
        date_str = self.current_date.toString("yyyy-MM-dd")
        hw_data = self.homework.get(date_str, {})
        self.homework_edit.setPlainText(hw_data.get(self.current_subject, ""))
        self.update_preview()

    def update_schedule(self):
        self.schedule_table.blockSignals(True)
        day_index = self.current_date.dayOfWeek() - 1
        day_name = DAYS_OF_WEEK[day_index] if day_index < len(DAYS_OF_WEEK) else ""
        
        schedule = self.get_schedule_for_date(self.current_date)
        subjects = schedule.get(day_name, [''] * MAX_LESSONS)
        
        self.day_of_week_label.setText(day_name)
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
                    latest_subjects = [str(s).strip() for s in subjects[:MAX_LESSONS]] + ['']*(MAX_LESSONS - len(subjects))
                    break
            schedule[day] = latest_subjects
        return schedule

    def prev_day(self):
        if not self.check_unsaved_changes(): 
            return
        self.current_date = self.current_date.addDays(-1)
        self.update_schedule()
        self._clear_selection()

    def next_day(self):
        if not self.check_unsaved_changes(): 
            return
        self.current_date = self.current_date.addDays(1)
        self.update_schedule()
        self._clear_selection()

    def _clear_selection(self):
        self.schedule_table.clearSelection()
        self.current_subject = None
        self.homework_edit.clear()
        self.preview_browser.clear()
        self.toggle_edit_btn.setEnabled(False)
        self.stack.setCurrentWidget(self.preview_browser)

    def mark_unsaved_changes(self):
        self.unsaved_changes = True

    def refresh_data(self):
        self.homework = self.data_manager.load_homework()
        self.update_schedule()
        self._clear_selection()
