from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger

class PEISException(Exception):
    """Base exception class for all PEIS errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ProjectNotFoundException(PEISException):
    def __init__(self, project_id: str):
        super().__init__(f"Project with ID '{project_id}' not found.", status_code=404)

class FileNotFoundException(PEISException):
    def __init__(self, file_path: str):
        super().__init__(f"File at path '{file_path}' not found.", status_code=404)

class ParsingException(PEISException):
    def __init__(self, file_path: str, details: str):
        super().__init__(f"Failed to parse file '{file_path}': {details}", status_code=422)

class LLMProviderException(PEISException):
    def __init__(self, provider: str, details: str):
        super().__init__(f"LLM Provider '{provider}' error: {details}", status_code=502)

class DatabaseException(PEISException):
    def __init__(self, details: str):
        super().__init__(f"Database operation failed: {details}", status_code=500)

class ValidationException(PEISException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ToolException(PEISException):
    def __init__(self, tool_name: str, message: str):
        super().__init__(f"Tool '{tool_name}' failed: {message}", status_code=500)

class AgentException(PEISException):
    def __init__(self, agent_name: str, message: str):
        super().__init__(f"Agent '{agent_name}' error: {message}", status_code=500)


def register_exception_handlers(app: FastAPI):
    """Registers global exception handlers to map custom errors into standard HTTP responses."""
    
    @app.exception_handler(PEISException)
    async def peis_exception_handler(request: Request, exc: PEISException):
        logger.error(f"PEIS Error [{exc.status_code}]: {exc.message} on request {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()} on request {request.url.path}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "RequestValidationError",
                "message": "Input request validation failed.",
                "details": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)} on request {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "InternalServerError",
                "message": "An unexpected error occurred in the application."
            }
        )
