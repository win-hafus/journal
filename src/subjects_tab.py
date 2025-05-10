from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QLineEdit, QPushButton, QLabel, QInputDialog, QMessageBox)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from .data_manager import DataManager

class SubjectsTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.subjects = self.data_manager.load_subjects()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.subject_list = QListWidget()
        self.subject_list.itemDoubleClicked.connect(self.edit_subject)
        
        layout.addWidget(QLabel("Список предметов:"))
        layout.addWidget(self.subject_list)
        layout.addLayout(self._create_control_layout())
        self.update_subject_list()
        self._apply_styles()
        self.setLayout(layout)

    def _create_control_layout(self):
        control_layout = QHBoxLayout()
        self.new_subject_input = QLineEdit()
        self.new_subject_input.setPlaceholderText("Новый предмет")
        
        add_btn = QPushButton("Добавить")
        remove_btn = QPushButton("Удалить")
        add_btn.clicked.connect(self.add_subject)
        remove_btn.clicked.connect(self.remove_subject)
        
        control_layout.addWidget(self.new_subject_input)
        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)
        return control_layout

    def _apply_styles(self):
        self.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            
            QListWidget::item:selected {
                background-color: #cce8ff;
                color: #000;
            }
            
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
            }
            
            QLineEdit:focus {
                border-color: #66afe9;
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
            
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)

    def update_subject_list(self):
        self.subject_list.clear()
        self.subject_list.addItems(self.subjects)

    def add_subject(self):
        new_subject = self.new_subject_input.text().strip().capitalize()
        if not new_subject: return
        
        existing_index = next((i for i, s in enumerate(self.subjects) if s.lower() == new_subject.lower()), -1)
        if existing_index != -1:
            self._highlight_duplicate(existing_index)
        else:
            self.subjects.append(new_subject)
            self.data_manager.save_subjects(self.subjects)
            self.update_subject_list()
            self.new_subject_input.clear()

    def remove_subject(self):
        selected = self.subject_list.currentRow()
        if selected >= 0:
            self.subjects.pop(selected)
            self.data_manager.save_subjects(self.subjects)
            self.update_subject_list()

    def edit_subject(self, item):
        old_text = item.text()
        new_text, ok = QInputDialog.getText(self, "Редактирование", "Новое название:", text=old_text)
        if ok and new_text.strip():
            new_text = new_text.strip().capitalize()
            if new_text == old_text: return
            
            duplicate_index = next((i for i, s in enumerate(self.subjects) if s.lower() == new_text.lower() and s != old_text), -1)
            if duplicate_index != -1:
                QMessageBox.warning(self, "Ошибка", "Такой предмет уже существует!")
                self._highlight_duplicate(duplicate_index)
            else:
                index = self.subjects.index(old_text)
                self.subjects[index] = new_text
                self.data_manager.save_subjects(self.subjects)
                self.update_subject_list()

    def _highlight_duplicate(self, index):
        self.subject_list.setCurrentRow(index)
        item = self.subject_list.item(index)
        item.setBackground(QColor("#cce8ff"))
        QTimer.singleShot(200, lambda: item.setBackground(QColor("#ffffff")))
    
    def refresh_data(self):
        self.subjects = self.data_manager.load_subjects()
        self.update_subject_list()
