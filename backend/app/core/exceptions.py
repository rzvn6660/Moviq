from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class MoviqException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": code,
                    "message": message,
                    "retryable": retryable,
                    "details": self.details,
                }
            },
        )


class EmptyPromptException(MoviqException):
    def __init__(self, message: str = "Prompt cannot be empty"):
        super().__init__(
            code="EMPTY_PROMPT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class PromptTooLongException(MoviqException):
    def __init__(self, max_length: int = 1000):
        super().__init__(
            code="PROMPT_TOO_LONG",
            message=f"Prompt exceeds maximum character length limit of {max_length} characters",
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class GenerationNotFoundException(MoviqException):
    def __init__(self, generation_id: str):
        super().__init__(
            code="GENERATION_NOT_FOUND",
            message=f"Generation with ID '{generation_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            retryable=False,
        )


class ModelNotFoundException(MoviqException):
    def __init__(self, model_id: str):
        super().__init__(
            code="MODEL_NOT_FOUND",
            message=f"Model with ID '{model_id}' is not supported or not found",
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class UnsupportedAspectRatioException(MoviqException):
    def __init__(self, aspect_ratio: str, model_id: str):
        super().__init__(
            code="UNSUPPORTED_ASPECT_RATIO",
            message=f"Aspect ratio '{aspect_ratio}' is not supported by model '{model_id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class UnsupportedDurationException(MoviqException):
    def __init__(self, duration: str, model_id: str):
        super().__init__(
            code="UNSUPPORTED_DURATION",
            message=f"Duration '{duration}' is not supported by model '{model_id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class NegativePromptNotSupportedException(MoviqException):
    def __init__(self, model_id: str):
        super().__init__(
            code="NEGATIVE_PROMPT_NOT_SUPPORTED",
            message=f"Negative prompt is not supported by model '{model_id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class ProviderFailureException(MoviqException):
    def __init__(self, provider_or_message: str, details: Optional[str] = None):
        msg = f"Provider '{provider_or_message}' failed generation request: {details}" if details else provider_or_message
        super().__init__(
            code="PROVIDER_FAILURE",
            message=msg,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class GenerationTimeoutException(MoviqException):
    def __init__(self, generation_id: str):
        super().__init__(
            code="GENERATION_TIMEOUT",
            message=f"Generation '{generation_id}' timed out during rendering execution",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            retryable=True,
        )


# Director Exceptions
class DirectorConfigurationErrorException(MoviqException):
    def __init__(self, message: str = "Groq API key or model configuration is missing"):
        super().__init__(
            code="DIRECTOR_CONFIGURATION_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=False,
        )


class DirectorProviderUnavailableException(MoviqException):
    def __init__(self, message: str = "AI Director service is temporarily unavailable"):
        super().__init__(
            code="DIRECTOR_PROVIDER_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=True,
        )


class DirectorTimeoutException(MoviqException):
    def __init__(self, message: str = "AI Director request timed out"):
        super().__init__(
            code="DIRECTOR_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            retryable=True,
        )


class DirectorRateLimitedException(MoviqException):
    def __init__(self, message: str = "AI Director rate limit exceeded. Please try again shortly."):
        super().__init__(
            code="DIRECTOR_RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            retryable=True,
        )


class DirectorInvalidResponseException(MoviqException):
    def __init__(self, message: str = "AI Director returned malformed or unparsable response"):
        super().__init__(
            code="DIRECTOR_INVALID_RESPONSE",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


# Fal Video Provider Exceptions
class FalConfigurationErrorException(MoviqException):
    def __init__(self, message: str = "FAL_KEY is not configured on backend server"):
        super().__init__(
            code="FAL_CONFIGURATION_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=False,
        )


class FalAuthenticationErrorException(MoviqException):
    def __init__(self, message: str = "FAL API key authentication failed"):
        super().__init__(
            code="FAL_AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            retryable=False,
        )


class FalRateLimitedException(MoviqException):
    def __init__(self, message: str = "fal-ai rate limit exceeded"):
        super().__init__(
            code="FAL_RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            retryable=True,
        )


class FalProviderUnavailableException(MoviqException):
    def __init__(self, message: str = "fal-ai service is temporarily unavailable"):
        super().__init__(
            code="FAL_PROVIDER_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=True,
        )


class FalSubmissionFailedException(MoviqException):
    def __init__(self, message: str = "Failed to submit video generation request to fal-ai"):
        super().__init__(
            code="FAL_SUBMISSION_FAILED",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class FalStatusErrorException(MoviqException):
    def __init__(self, message: str = "Failed to query status from fal-ai queue"):
        super().__init__(
            code="FAL_STATUS_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class FalResultErrorException(MoviqException):
    def __init__(self, message: str = "fal-ai video result payload was invalid or missing video URL"):
        super().__init__(
            code="FAL_RESULT_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class DuplicateSubmissionException(MoviqException):
    def __init__(self, message: str = "Duplicate generation request detected via idempotency key"):
        super().__init__(
            code="DUPLICATE_SUBMISSION",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            retryable=False,
        )


class ValidationErrorException(MoviqException):
    def __init__(self, message: str):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            retryable=False,
        )


# Hugging Face Video Provider Exceptions
class HFConfigurationErrorException(MoviqException):
    def __init__(self, message: str = "HF_TOKEN is not configured on backend server"):
        super().__init__(
            code="HF_CONFIGURATION_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=False,
        )


class HFAuthenticationErrorException(MoviqException):
    def __init__(self, message: str = "Hugging Face API token authentication failed"):
        super().__init__(
            code="HF_AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            retryable=False,
        )


class HFRateLimitedException(MoviqException):
    def __init__(self, message: str = "Hugging Face rate limit exceeded. Please try again later."):
        super().__init__(
            code="HF_RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            retryable=True,
        )


class HFInsufficientCreditsException(MoviqException):
    def __init__(self, message: str = "Hugging Face account has insufficient inference credits"):
        super().__init__(
            code="HF_INSUFFICIENT_CREDITS",
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            retryable=False,
        )


class HFModelUnavailableException(MoviqException):
    def __init__(self, message: str = "Selected Hugging Face model is currently unavailable"):
        super().__init__(
            code="HF_MODEL_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=True,
        )


class HFProviderUnavailableException(MoviqException):
    def __init__(self, message: str = "Hugging Face inference service is temporarily unavailable"):
        super().__init__(
            code="HF_PROVIDER_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=True,
        )


class HFGenerationFailedException(MoviqException):
    def __init__(self, message: str = "Hugging Face video generation failed"):
        super().__init__(
            code="HF_GENERATION_FAILED",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class HFInvalidResultException(MoviqException):
    def __init__(self, message: str = "Hugging Face video result payload was invalid or empty"):
        super().__init__(
            code="HF_INVALID_RESULT",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class HFTimeoutException(MoviqException):
    def __init__(self, message: str = "Hugging Face inference request timed out"):
        super().__init__(
            code="HF_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            retryable=True,
        )


# Wan2.1 Open-Source Video Provider Exceptions
class WANDependenciesMissingException(MoviqException):
    def __init__(self, message: str = "Wan2.1 dependencies (torch, diffusers, transformers) are not installed in the environment"):
        super().__init__(
            code="WAN_DEPENDENCIES_MISSING",
            message=message,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            retryable=False,
        )


class WANCUDAUnavailableException(MoviqException):
    def __init__(self, message: str = "CUDA GPU device is unavailable for local Wan2.1 inference"):
        super().__init__(
            code="WAN_CUDA_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=False,
        )


class WANModelLoadFailedException(MoviqException):
    def __init__(self, message: str = "Failed to load Wan2.1 model weights into GPU memory"):
        super().__init__(
            code="WAN_MODEL_LOAD_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=True,
        )


class WANOutOfMemoryException(MoviqException):
    def __init__(self, message: str = "CUDA out of memory during Wan2.1 diffusion step execution"):
        super().__init__(
            code="WAN_OUT_OF_MEMORY",
            message=message,
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            retryable=True,
        )


class WANGenerationFailedException(MoviqException):
    def __init__(self, message: str = "Wan2.1 video generation failed during execution"):
        super().__init__(
            code="WAN_GENERATION_FAILED",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class WANInvalidOutputException(MoviqException):
    def __init__(self, message: str = "Wan2.1 video output render was empty or invalid"):
        super().__init__(
            code="WAN_INVALID_OUTPUT",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


# Remote Wan2.1 GPU Worker Exceptions
class RemoteWANConfigurationErrorException(MoviqException):
    def __init__(self, message: str = "REMOTE_WAN_URL is not configured on the backend server"):
        super().__init__(
            code="REMOTE_WAN_CONFIGURATION_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=False,
        )


class RemoteWANUnavailableException(MoviqException):
    def __init__(self, message: str = "Remote Wan2.1 GPU worker is unreachable or offline"):
        super().__init__(
            code="REMOTE_WAN_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            retryable=True,
        )


class RemoteWANTimeoutException(MoviqException):
    def __init__(self, message: str = "Remote Wan2.1 GPU worker request timed out"):
        super().__init__(
            code="REMOTE_WAN_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            retryable=True,
        )


class RemoteWANAuthenticationErrorException(MoviqException):
    def __init__(self, message: str = "Authentication with remote Wan2.1 GPU worker failed"):
        super().__init__(
            code="REMOTE_WAN_AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            retryable=False,
        )


class RemoteWANGenerationFailedException(MoviqException):
    def __init__(self, message: str = "Remote Wan2.1 GPU worker reported a generation error"):
        super().__init__(
            code="REMOTE_WAN_GENERATION_FAILED",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )


class RemoteWANInvalidResultException(MoviqException):
    def __init__(self, message: str = "Result payload or downloaded video from remote Wan2.1 worker was invalid"):
        super().__init__(
            code="REMOTE_WAN_INVALID_RESULT",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=True,
        )



