from rest_framework.exceptions import NotFound
from rest_framework import status


class ProfileDoesNotExistException(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "Profile doesn't exist"
