from admin_portal.models import AdminLog

def log_admin_action(user, action):
    """
    Centralized function to log admin actions.
    :param user: The admin user performing the action.
    :param action: Description of the action performed.
    """
    if not user or not action:
        raise ValueError("User and action must be provided for logging.")

    AdminLog.objects.create(user=user, action=action)
    print(f"Log created: {user.email} - {action}")
