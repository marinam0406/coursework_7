from datetime import datetime, timedelta

import pytz
from celery import shared_task

from config import settings
from habits.models import Habit
from habits.services import send_telegram_message
from users.models import User


@shared_task
def send_remainder():
    habits = Habit.objects.all()
    users = User.objects.all()
    for user in users:
        if user.tg_chat_id:
            for habit in habits:
                habit_start_time = habit.time.replace(second=0, microsecond=0)
                habit_time_now = datetime.now(
                    pytz.timezone(settings.TIME_ZONE)
                ).replace(second=0, microsecond=0)
                if habit_start_time == habit_time_now:
                    if habit.pleasant_habit_sign:
                        send_telegram_message(
                            habit.owner.tg_chat_id,
                            f"Сделай: {habit.action}, "
                            f"за: {habit.duration} минут.",
                        )
                    if habit.related_habit:
                        send_telegram_message(
                            habit.owner.tg_chat_id,
                            f"Сделай: {habit.action}, "
                            f"за: {habit.duration} минут, "
                            f"и тогда можешь: {habit.related_habit}.",
                        )
                    if habit.reward:
                        send_telegram_message(
                            habit.owner.tg_chat_id,
                            f"Сделай: {habit.action}, "
                            f"за: {habit.duration} минут, "
                            f"и получишь в награду: {habit.reward}.",
                        )
                    habit.time = datetime.now(
                        pytz.timezone(settings.TIME_ZONE)
                    ) + timedelta(days=habit.periodicity)
                    habit.save()
