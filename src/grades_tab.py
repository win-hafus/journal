from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QDialog, QListWidget, 
    QDialogButtonBox, QButtonGroup, QComboBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from .data_manager import DataManager

class GradesTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.grades = self._safe_load_grades()
        self.hidden_subjects = set(self.data_manager.load_hidden_subjects())
        self.term_days = [53, 44, 59, 45]
        self.current_term = 0
        self.grade_options = ['', '2', '3', '4', '5', 'Н', 'Б']
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self._setup_table_columns()
        layout.addLayout(self._create_control_layout())
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.update_table()
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet("""
            QPushButton {
                font-size: 10pt;
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
                qproperty-alignment: AlignCenter;
            }
            
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
            
            QComboBox QAbstractItemView {
                font-size: 12pt;
                padding: 10px;
                border: 1px solid #ccc;
                background-color: #fff;
                selection-background-color: #cce8ff;
            }
        """)

    def _create_control_layout(self):
        control_layout = QHBoxLayout()
        self.term_buttons = QButtonGroup()
        for i in range(4):
            btn = QPushButton(f"{i+1} четверть")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, idx=i: self.set_current_term(idx))
            control_layout.addWidget(btn)
            self.term_buttons.addButton(btn, i)
        self.hide_btn = QPushButton("Скрыть")
        self.show_hidden_btn = QPushButton("Показать скрытые")
        self.hide_btn.setFixedSize(150, 40)
        self.show_hidden_btn.setFixedSize(200, 40)
    
        # Добавьте подключение сигналов
        self.hide_btn.clicked.connect(self.hide_subject)
        self.show_hidden_btn.clicked.connect(self.show_hidden_dialog)
    
        control_layout.addStretch()
        control_layout.addWidget(self.show_hidden_btn)
        control_layout.addWidget(self.hide_btn)
        self.term_buttons.buttons()[0].setChecked(True)
        return control_layout

    def _setup_table_columns(self):
        max_visible = self._calculate_max_columns()
        columns = ["Предмет"] + [f"{i+1}" for i in range(max_visible)] + ["Среднее"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setColumnWidth(0, 200)
        for i in range(1, len(columns)-1):
            self.table.setColumnWidth(i, 60)
        self.table.setColumnWidth(len(columns)-1, 100)

    def _calculate_max_columns(self):
        max_days = self.term_days[self.current_term]
        max_filled = 1
        for subject in self.grades.values():
            if not isinstance(subject, list) or len(subject) != 4:
                continue
            term_grades = subject[self.current_term] if len(subject) > self.current_term else []
            if not isinstance(term_grades, list):
                continue
            filled = len([g for g in term_grades if g])
            max_filled = max(max_filled, filled + 1)
        return min(max_filled, max_days)

    def _calculate_average(self, subject):
        grades = self.grades.get(subject, [[], [], [], []])
        if not isinstance(grades, list) or len(grades) != 4:
            return "0.00"
        term_grades = grades[self.current_term] if len(grades) > self.current_term else []
        if not isinstance(term_grades, list):
            return "0.00"
        valid = [float(v) for v in term_grades if v and str(v).replace('.', '', 1).isdigit()]
        return f"{sum(valid)/len(valid):.2f}" if valid else "0.00"

    def _restore_subjects(self, list_widget, dialog):
        selected = list_widget.selectedItems()
        for item in selected:
            self.hidden_subjects.remove(item.text())
        self.data_manager.save_hidden_subjects(list(self.hidden_subjects))
        self.update_table()
        dialog.accept()

    def _safe_load_grades(self):
        raw_grades = self.data_manager.load_grades()
        for subject in raw_grades:
            if not isinstance(raw_grades[subject], list) or len(raw_grades[subject]) != 4:
                raw_grades[subject] = [[], [], [], []]
            for i in range(4):
                if not isinstance(raw_grades[subject][i], list):
                    raw_grades[subject][i] = []
        return raw_grades

    def update_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        subjects = [s for s in self.data_manager.load_subjects() if s not in self.hidden_subjects]
        self.table.setRowCount(len(subjects))
        max_columns = self._calculate_max_columns()

        for row, subject in enumerate(subjects):
            subject_item = QTableWidgetItem(subject)
            subject_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, subject_item)

            grades = self.grades.get(subject, [[], [], [], []])
            term_grades = grades[self.current_term] if len(grades) > self.current_term else []

            for col in range(1, max_columns + 1):
                combo = QComboBox()
                combo.addItems(self.grade_options)
                value = term_grades[col-1] if (col-1) < len(term_grades) else ''
                index = combo.findText(value)
                combo.setCurrentIndex(index if index != -1 else 0)
                combo.currentTextChanged.connect(lambda text, r=row, c=col: self.on_grade_changed(text, r, c))
                self.table.setCellWidget(row, col, combo)

            avg_item = QTableWidgetItem(self._calculate_average(subject))
            avg_item.setTextAlignment(Qt.AlignCenter)
            avg_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, max_columns + 1, avg_item)

        self.table.blockSignals(False)
        self.update_buttons_state()

    def on_grade_changed(self, value, row, column):
        subject = self.table.item(row, 0).text()
        day_idx = column - 1
        if subject not in self.grades:
            self.grades[subject] = [[], [], [], []]
        grades = self.grades[subject]
        if not isinstance(grades, list) or len(grades) != 4:
            grades = [[], [], [], []]
            self.grades[subject] = grades
        term_grades = grades[self.current_term]
        if not isinstance(term_grades, list):
            term_grades = []
            grades[self.current_term] = term_grades
        while len(term_grades) < day_idx + 1:
            term_grades.append('')
        term_grades[day_idx] = value
        term_grades[:] = term_grades[:self.term_days[self.current_term]]
        self.data_manager.save_grades(self.grades)
    
        prev_max = self._calculate_max_columns()
        self._setup_table_columns()
        current_max = self._calculate_max_columns()
        if current_max != prev_max:
            self.update_table()
        else:
            avg_col = self.table.columnCount() - 1
            avg_item = self.table.item(row, avg_col)
            if avg_item is not None:
                avg_item.setText(self._calculate_average(subject))
    
        if column == self._calculate_max_columns():
            self._setup_table_columns()
            self.update_table()

    def show_hidden_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Скрытые предметы")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.addItems(self.hidden_subjects)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self._restore_subjects(list_widget, dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(list_widget)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec_()

    def hide_subject(self):
        row = self.table.currentRow()
        if row >= 0:
            subject = self.table.item(row, 0).text()
            self.hidden_subjects.add(subject)
            self.data_manager.save_hidden_subjects(list(self.hidden_subjects))
            self.update_table()

    def update_buttons_state(self):
        self.show_hidden_btn.setEnabled(len(self.hidden_subjects) > 0)

    def refresh_data(self):
        self.grades = self._safe_load_grades()
        self.hidden_subjects = set(self.data_manager.load_hidden_subjects())
        self.update_table()

    def set_current_term(self, term_idx):
        self.current_term = term_idx
        self._setup_table_columns()
        self.update_table()
