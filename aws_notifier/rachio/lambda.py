from datetime import datetime


def handler(event, context):
    print(f"run cron job {datetime.now().time()}")
