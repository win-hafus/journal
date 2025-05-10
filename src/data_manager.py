from PyQt5.QtCore import QObject, pyqtSignal
import json

DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
MAX_LESSONS = 9

class DataManager(QObject):
    subjects_updated = pyqtSignal()
    schedule_updated = pyqtSignal()
    homework_updated = pyqtSignal()
    grades_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.schedule_file = 'data/schedule.json'
        self.homework_file = 'data/homework.json'
        self.subjects_file = 'data/subjects.json'
        self.grades_file = 'data/grades.json'
        self.hidden_subjects_file = 'data/hidden_subjects.json'

    def load_subjects(self):
        try:
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_subjects(self, data):
        with open(self.subjects_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.subjects_updated.emit()

    def load_schedule(self):
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for day in DAYS_OF_WEEK:
                    if day in data and isinstance(data[day], list):
                        if all(isinstance(item, str) for item in data[day]):
                            data[day] = [{
                                "start_date": "1970-01-01",
                                "subjects": data[day] + ['']*(MAX_LESSONS - len(data[day]))
                            }]
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {day: [{"start_date": "2024-01-01", "subjects": ['']*MAX_LESSONS}] for day in DAYS_OF_WEEK}

    def save_schedule(self, data):
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.schedule_updated.emit()

    def load_homework(self):
        try:
            with open(self.homework_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_homework(self, data):
        with open(self.homework_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.homework_updated.emit()
    
    def load_grades(self):
        try:
            with open(self.grades_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {subject: list(grades.values()) for subject, grades in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_grades(self, data):
        formatted_data = {subject: {f"grade_{i}": grade for i, grade in enumerate(grades)} 
                        for subject, grades in data.items()}
        with open(self.grades_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        self.grades_updated.emit()

    def load_hidden_subjects(self):
        try:
            with open(self.hidden_subjects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_hidden_subjects(self, hidden_subjects):
        with open(self.hidden_subjects_file, 'w', encoding='utf-8') as f:
            json.dump(hidden_subjects, f, ensure_ascii=False, indent=2)
