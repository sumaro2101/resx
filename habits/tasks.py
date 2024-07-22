from config.celery import app
from habits.services import construct_message


@app.task
def send_habit_raminder(id_habit: str, id_chat: str):
    """Точка отравки задачи для напоминания
    """
    construct_message(id_habit, id_chat)
