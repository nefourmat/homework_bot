class InvalidTokens(Exception):
    """Error in environment variables."""
    pass


class ResponseErrorException(Exception):
    pass


class InvalidResponseCode(Exception):
    pass


class TelegramBadRequest(Exception):
    pass
