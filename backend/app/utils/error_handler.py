from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import RequestValidationError

class NotFoundError(Exception):
    """Exception raised when a resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = f"{resource_type} not found with identifier: {resource_id}"
        super().__init__(self.message)

class DataProcessingError(Exception):
    """Exception raised when there's an issue processing data."""
    pass

async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handler for resource not found exceptions."""
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "resource_type": exc.resource_type, "resource_id": exc.resource_id}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation errors."""
    errors = []
    for error in exc.errors():
        location = error.get("loc", [])
        field = location[-1] if len(location) > 0 else "unknown"
        message = error.get("msg", "Unknown validation error")
        errors.append({"field": field, "message": message})
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error in request",
            "errors": errors
        }
    )

async def data_processing_exception_handler(request: Request, exc: DataProcessingError):
    """Handler for data processing errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

def register_exception_handlers(app):
    """Register all custom exception handlers with the FastAPI app."""
    app.add_exception_handler(NotFoundError, not_found_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DataProcessingError, data_processing_exception_handler)