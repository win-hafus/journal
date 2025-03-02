from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class SubjectsTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.subjects = self.data_manager.load_subjects()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Список предметов
        self.subject_list = QListWidget()
        self.subject_list.itemDoubleClicked.connect(self.edit_subject)
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        self.new_subject_input = QLineEdit()
        self.new_subject_input.setPlaceholderText("Новый предмет")
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_subject)
        
        remove_btn = QPushButton("Удалить")
        remove_btn.clicked.connect(self.remove_subject)
        
        control_layout.addWidget(self.new_subject_input)
        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)
        
        layout.addWidget(QLabel("Список предметов:"))
        layout.addWidget(self.subject_list)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        self.update_subject_list()
        
        # Применение стилей
        self.setStyleSheet("""
            /* Стилизация QListWidget (список предметов) */
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
            
            /* Стилизация QLineEdit (поле ввода) */
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
            
            /* Стилизация QLabel (метка) */
            QLabel {
                font-size: 14px;
                color: #333;
            }
        """)
        
    def update_subject_list(self):
        self.subject_list.clear()
        self.subject_list.addItems(self.subjects)
        
    def add_subject(self):
        new_subject = self.new_subject_input.text().strip()
        if new_subject and new_subject not in self.subjects:
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
        new_text, ok = QInputDialog.getText(
            self, 
            "Редактирование предмета", 
            "Новое название:", 
            text=old_text
        )
        if ok and new_text.strip():
            index = self.subjects.index(old_text)
            self.subjects[index] = new_text.strip()
            self.data_manager.save_subjects(self.subjects)
            self.update_subject_list()
