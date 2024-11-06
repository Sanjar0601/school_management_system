from background_task import background

@background(schedule=60)
def my_scheduled_task():
    print("Executing scheduled task now")