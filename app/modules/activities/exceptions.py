from fastapi import status

from app.exceptions.base import AppBaseException


class ActivityException(AppBaseException):
    """Base exception for all activity-related errors."""


class ActivityDateOutOfRangeException(ActivityException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "ACTIVITY_DATE_OUT_OF_RANGE"
    message = "Activity date must fall within the trip dates."