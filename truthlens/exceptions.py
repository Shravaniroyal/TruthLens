"""Custom exceptions — each maps to a user-safe error message in the UI."""


class TruthLensError(Exception):
    """Base class for all TruthLens application errors."""

    user_message: str = "An unexpected error occurred. Please try again."

    def __init__(self, message: str = "", *, user_message: str | None = None):
        super().__init__(message or self.user_message)
        if user_message is not None:
            self.user_message = user_message


class ModelLoadError(TruthLensError):
    """Raised when model weights cannot be loaded."""

    user_message = "The fraud detection model could not be loaded. Check model path and logs."


class SecurityValidationError(TruthLensError):
    """Raised when an uploaded file fails security checks."""

    user_message = "The uploaded file did not pass security validation."


class ImageProcessingError(TruthLensError):
    """Raised when an image cannot be decoded or processed."""

    user_message = "Could not read the uploaded file. Please upload a valid image."


class AnalysisError(TruthLensError):
    """Raised when inference or explainability steps fail."""

    user_message = "Document analysis failed. Please try again or use a different file."


class AuthError(TruthLensError):
    """Raised when API authentication fails."""

    user_message = "Invalid or missing API key."
