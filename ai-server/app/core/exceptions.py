class AIServerError(Exception):
    """모든 AI 서버 관련 예외의 기본 클래스"""
    status_code = 500
    error_code = "AI_SERVER_ERROR"

    def __init__(self, message="AI server error"):
        self.message = message
        super().__init__(message)


class GenerationError(AIServerError):
    """음악 생성 실패"""
    status_code = 500
    error_code = "MUSIC_GENERATION_FAILED"

    def __init__(self, message="Music generation failed"):
        super().__init__(message)


class S3UploadError(AIServerError):
    """S3 업로드 실패"""
    status_code = 502
    error_code = "S3_UPLOAD_FAILED"

    def __init__(self, message="S3 upload failed"):
        super().__init__(message)


class InvalidPromptError(AIServerError):
    """프롬프트가 비정상적인 경우"""
    status_code = 400
    error_code = "INVALID_PROMPT"

    def __init__(self, message="Invalid prompt for music generation"):
        super().__init__(message)
