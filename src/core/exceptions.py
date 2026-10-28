from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

class DomainError(Exception):
    """Base exception for all domain-specific errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class ResourceNotFoundError(DomainError):
    pass

class ValidationError(DomainError):
    pass

class InvalidTimeRangeError(ValidationError):
    pass

class MaxDurationExceededError(ValidationError):
    pass

class ReservationConflictError(DomainError):
    pass

class ActiveReservationLimitError(DomainError):
    pass

class CancellationWindowExpiredError(DomainError):
    pass

class InvalidReservationStateError(DomainError):
    pass

class AuthenticationError(DomainError):
    pass

class PermissionDeniedError(DomainError):
    pass

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.message, "error_type": "NOT_FOUND"}
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_type": "VALIDATION_ERROR"}
        )

    @app.exception_handler(ReservationConflictError)
    async def conflict_error_handler(request: Request, exc: ReservationConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message, "error_type": "RESERVATION_CONFLICT"}
        )

    @app.exception_handler(ActiveReservationLimitError)
    async def active_limit_handler(request: Request, exc: ActiveReservationLimitError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": exc.message, "error_type": "ACTIVE_RESERVATION_LIMIT"}
        )

    @app.exception_handler(CancellationWindowExpiredError)
    async def cancellation_expired_handler(request: Request, exc: CancellationWindowExpiredError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_type": "CANCELLATION_WINDOW_EXPIRED"}
        )

    @app.exception_handler(InvalidReservationStateError)
    async def invalid_state_handler(request: Request, exc: InvalidReservationStateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message, "error_type": "INVALID_STATE"}
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
            content={"detail": exc.message, "error_type": "UNAUTHORIZED"}
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.message, "error_type": "FORBIDDEN"}
        )
