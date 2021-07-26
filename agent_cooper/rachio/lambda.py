import datetime
import os

import pytz

import aws
from rachio import Rachio

PROJECT_NAME = os.getenv("PROJECT_NAME")
STAGE = os.getenv("STAGE")


def handler(event, context):
    find_tomorrow_schedule()
    print(f"run cron job {datetime.datetime.now().time()}")


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
    rachio_api_key = aws.parameter_store.get_parameter(
        f"/{PROJECT_NAME}/{STAGE}/rachio/api_key")
    # use pytz.common_timezones to list all common timezones
    rachio_time_zone = aws.parameter_store.get_parameter(
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
        name = schedule.get("scheduleName", "??")
        start_time = schedule.get("startTime", {"hour": "??", "minute": "??"})
        end_time = schedule.get("endTime", {"hour": "??", "minute": "??"})

        print(f"{date['month']}-{date['day']}")
        print(f"{name}")
        print(
            f"from {start_time['hour']}:{start_time['second']} to "
            f"{end_time['hour']}:{end_time['second']}")

        return "something tuple"
    else:
        print("no watering schedule")

        return None
