class APIRequestError(ConnectionError):
    """
    Raised when an HTTP request fails.
    """

    def __init__(self, method: str, path: str, status_code: int, response: str):
        message = (
            "[ERROR] - Something went wrong with the request\n"
            f"Method: {method}\n"
            f"Path: {path}\n"
            f"Status code: {status_code}\n"
            f"Response: {response}\n"
        )
        super().__init__(message)


class APIBadResponseError(ConnectionError):
    """
    Raised when API response structure/content is invalid.
    """

    def __init__(self, path: str):
        message = (
            "[BAD RESPONSE FROM API]\n"
            f"The call to {path} did not return a correct response\n"
        )
        super().__init__(message)
