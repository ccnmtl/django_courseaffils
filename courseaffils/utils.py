from django.utils import timezone


SPRING = 1
SUMMER = 2
FALL = 3


def get_current_term():
    """Find out what semester we're currently in.

    Return values are:
    1 - Spring
    2 - Summer
    3 - Fall
    """
    today = timezone.now().date()

    # Assume that schools start summer semester in the second half
    # of May or later.
    if today.month <= 4 or (today.month == 5 and today.day <= 15):
        return SPRING
    elif today.month <= 8:
        return SUMMER
    else:
        return FALL
