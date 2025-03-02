import json

DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
MAX_LESSONS = 9

class DataManager:
    def __init__(self):
        self.schedule_file = '../data/schedule.json'
        self.homework_file = '../data/homework.json'
        self.subjects_file = '../data/subjects.json'
        
    def load_schedule(self):
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Конвертация старого формата в новый
                for day in DAYS_OF_WEEK:
                    if day in data and isinstance(data[day], list):
                        # Если данные в старом формате [subjects]
                        if all(isinstance(item, str) for item in data[day]):
                            data[day] = [{
                                "start_date": "1970-01-01",
                                "subjects": data[day] + ['']*(MAX_LESSONS - len(data[day]))
                            }]
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # Создаем новую структуру данных
            return {day: [{
                "start_date": "1970-01-01",
                "subjects": ['']*MAX_LESSONS
            }] for day in DAYS_OF_WEEK}
            
    def save_schedule(self, data):
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_homework(self):
        try:
            with open(self.homework_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def save_homework(self, data):
        with open(self.homework_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_subjects(self):
        try:
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
    def save_subjects(self, data):
        with open(self.subjects_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
