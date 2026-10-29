from fastapi import status


class APIError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class BadRequestError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundError(APIError):
    status_code = status.HTTP_404_NOT_FOUND
