from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.data_manager import DataManager

app = FastAPI(title="Journal API", description="REST API для школьного дневника")

DAYS_OF_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

dm = DataManager()

class SubjectsPayload(BaseModel):
    subjects: list[str]

class SchedulePayload(BaseModel):
    schedule: dict

class HomeworkDayPayload(BaseModel):
    homework: dict  # { "Математика": "стр. 42", ... }

class GradesPayload(BaseModel):
    grades: list    # [5, 4, 3, ...]

# Список предметов

@app.get("/subjects", summary="Получить список предметов")
def get_subjects():
    return {"subjects": dm.load_subjects()}

@app.put("/subjects", summary="Обновить список предметов целиком")
def update_subjects(payload: SubjectsPayload):
    dm.save_subjects(payload.subjects)
    return {"ok": True, "subjects": payload.subjects}

@app.post("/subjects", summary="Добавить предмет")
def add_subject(payload: dict):
    name = payload.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Поле 'name' обязательно")
    subjects = dm.load_subjects()
    if name in subjects:
        raise HTTPException(status_code=409, detail="Предмет уже существует")
    subjects.append(name)
    dm.save_subjects(subjects)
    return {"ok": True, "subjects": subjects}

@app.delete("/subjects/{name}", summary="Удалить предмет")
def delete_subject(name: str):
    subjects = dm.load_subjects()
    if name not in subjects:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    subjects.remove(name)
    dm.save_subjects(subjects)
    return {"ok": True, "subjects": subjects}

# Домашние задания

@app.get("/homework", summary="Получить все домашние задания")
def get_homework():
    return {"homework": dm.load_homework()}

@app.get("/homework/{date}", summary="Получить домашнее задание на дату (формат: YYYY-MM-DD)")
def get_homework_by_date(date: str):
    homework = dm.load_homework()
    if date not in homework:
        raise HTTPException(status_code=404, detail=f"Нет домашнего задания на {date}")
    return {"date": date, "homework": homework[date]}

@app.put("/homework/{date}", summary="Обновить домашнее задание на дату")
def update_homework_by_date(date: str, payload: HomeworkDayPayload):
    homework = dm.load_homework()
    homework[date] = payload.homework
    dm.save_homework(homework)
    return {"ok": True, "date": date, "homework": payload.homework}

@app.delete("/homework/{date}", summary="Удалить домашнее задание на дату")
def delete_homework_by_date(date: str):
    homework = dm.load_homework()
    if date not in homework:
        raise HTTPException(status_code=404, detail=f"Нет домашнего задания на {date}")
    del homework[date]
    dm.save_homework(homework)
    return {"ok": True}

# Оценки

@app.get("/grades", summary="Получить все оценки")
def get_grades():
    return {"grades": dm.load_grades()}

@app.get("/grades/{subject}", summary="Получить оценки по предмету")
def get_grades_by_subject(subject: str):
    grades = dm.load_grades()
    if subject not in grades:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return {"subject": subject, "grades": grades[subject]}

@app.put("/grades/{subject}", summary="Обновить оценки по предмету")
def update_grades_by_subject(subject: str, payload: GradesPayload):
    grades = dm.load_grades()
    grades[subject] = payload.grades
    dm.save_grades(grades)
    return {"ok": True, "subject": subject, "grades": payload.grades}

@app.delete("/grades/{subject}", summary="Удалить оценки по предмету")
def delete_grades_by_subject(subject: str):
    grades = dm.load_grades()
    if subject not in grades:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    del grades[subject]
    dm.save_grades(grades)
    return {"ok": True}

# Расписание

@app.get("/schedule", summary="Получить расписание на всю неделю")
def get_schedule():
    return {"schedule": dm.load_schedule()}

@app.get("/schedule/{day}", summary="Получить расписание на день")
def get_schedule_by_day(day: str):
    if day not in DAYS_OF_WEEK:
        raise HTTPException(status_code=422, detail=f"Неверный день. Доступны: {DAYS_OF_WEEK}")
    schedule = dm.load_schedule()
    if day not in schedule:
        raise HTTPException(status_code=404, detail="Расписание для этого дня не найдено")
    return {"day": day, "schedule": schedule[day]}

@app.put("/schedule", summary="Обновить расписание целиком")
def update_schedule(payload: SchedulePayload):
    dm.save_schedule(payload.schedule)
    return {"ok": True}