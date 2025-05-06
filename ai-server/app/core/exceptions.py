class AIServerError(Exception):
    status_code = 500

    def __init__(self, message="AI server error"):
        self.message = message
        super().__init__(message)


class GenerationError(AIServerError):
    def __init__(self, message="Music generation failed"):
        super().__init__(message)