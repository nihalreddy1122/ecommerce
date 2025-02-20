from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Define an interval (e.g., every 1 minute)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.MINUTES,
)

# Create or update the periodic task
PeriodicTask.objects.update_or_create(
    name='Send Abandoned Cart Reminder',
    defaults={
        'interval': schedule,
        'task': 'cart_orders.tasks.send_abandoned_cart_reminders',  # Update the task path if necessary
        'args': json.dumps([]),  # Optional arguments
        'kwargs': json.dumps({}),  # Optional keyword arguments
    }
)
