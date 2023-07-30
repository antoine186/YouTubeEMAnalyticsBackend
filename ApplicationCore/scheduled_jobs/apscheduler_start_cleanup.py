import atexit
from app_start_helper import scheduler

def apscheduler_start_cleanup():
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())