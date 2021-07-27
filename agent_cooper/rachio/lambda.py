import datetime
import os

import pytz

from client.aws import ParameterStore
from client.google import Gmail
from client.rachio import Rachio

PROJECT_NAME = os.getenv("PROJECT_NAME")
STAGE = os.getenv("STAGE")
AWS_REGION = os.getenv("AWS_REGION")


def handler(event, context):
    print(f"run cron job {datetime.datetime.now().time()}")

    schedule = find_tomorrow_schedule()

    if schedule:
        print("Found a schedule that is going to run soon")

        schedule_name = schedule["schedule_name"]
        date = schedule["date"]
        start = schedule["start_time"]
        end = schedule["end_time"]

        subject = "Rachio is going to water your lawn"
        msg = f"Schedule ({schedule_name}) is going to run from {start} to {end} on " \
              f"{date}"

        send_email_notification(subject, msg)


def _get_scheduler_range(timezone="America/Chicago", timedelta=1, range=1):
    midnight = (datetime.datetime
                .now(pytz.timezone(timezone))
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .astimezone(pytz.timezone('UTC'))
                )

    start = midnight + datetime.timedelta(days=timedelta)
    end = midnight + datetime.timedelta(days=timedelta + range)

    return start, end


def find_tomorrow_schedule():
    parameter_store = ParameterStore(AWS_REGION)

    rachio_api_key = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/rachio/api_key")
    # use pytz.common_timezones to list all common timezones
    rachio_time_zone = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/rachio/time_zone")
    (start_of_tomorrow, end_of_tomorrow) = _get_scheduler_range(
        timezone=rachio_time_zone, timedelta=1, range=1)

    client = Rachio(api_key=rachio_api_key)
    user_id = client.get_user_id()
    device_id = client.get_device_id(user_id)
    location_id = client.get_location_id(device_id)

    schedules = client.get_schedules(
        location_id=location_id,
        start_time=start_of_tomorrow,
        end_time=end_of_tomorrow,
    )

    if "wateringDay" in schedules and schedules["wateringDay"]:
        schedule = schedules["wateringDay"][0]

        date = schedule.get("date", {"month": "??", "day": "??"})
        schedule_name = schedule.get("scheduleName", "??")
        start_time = schedule.get("startTime", {"hour": "??", "minute": "??"})
        end_time = schedule.get("endTime", {"hour": "??", "minute": "??"})

        return {
            "date": f"{date['month']}-{date['day']}",
            "schedule_name": schedule_name,
            "start_time": f"{start_time['hour']}:{start_time['second']}",
            "end_time": f"{end_time['hour']}:{end_time['second']}",
        }
    else:
        print("no watering schedule")

        return None


def send_email_notification(subject, msg):
    parameter_store = ParameterStore(AWS_REGION)

    gmail_client_id = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/gmail/client_id")
    gmail_client_secret = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/gmail/client_secret")
    gmail_refresh_token = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/gmail/refresh_token")
    gmail_address = parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/gmail/address")

    gmail = Gmail(
        client_id=gmail_client_id,
        client_secret=gmail_client_secret,
        refresh_token=gmail_refresh_token,
    )

    gmail.send_message(sender=gmail_address, to=gmail_address,
                       subject=subject,
                       msg=msg)
