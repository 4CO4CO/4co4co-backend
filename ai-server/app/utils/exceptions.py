class AIServerError(Exception):

    status_code = 500
    error_code = "AI_SERVER_ERROR"

    def __init__(self, message="AI server error"):
        self.message = message
        super().__init__(message)


class GenerationError(AIServerError):

    status_code = 500
    error_code = "MUSIC_GENERATION_FAILED"

    def __init__(self, message="Music generation failed"):
        super().__init__(message)


class S3UploadError(AIServerError):
    """
    Exception raised when uploading a file to S3 fails.
    """
    status_code = 502
    error_code = "S3_UPLOAD_FAILED"

    def __init__(self, message="S3 upload failed"):
        super().__init__(message)


class InvalidPromptError(AIServerError):
    """
    Exception raised when the provided prompt is invalid
    for music generation.
    """
    status_code = 400
    error_code = "INVALID_PROMPT"

    def __init__(self, message="Invalid prompt for music generation"):
        super().__init__(message)
