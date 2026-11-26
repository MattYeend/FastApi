from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes import products, users
from app.core.config import settings
from app.core.exceptions import DomainError, domain_error_handler
from app.dependencies.auth import require_api_key
from app.dependencies.database import get_db
from app.middleware.security_headers import SecurityHeadersMiddleware

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="User and product management API",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_exception_handler(DomainError, domain_error_handler)

app.include_router(
    users.router,
    prefix="/api/v1",
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    products.router,
    prefix="/api/v1",
    dependencies=[Depends(require_api_key)],
)


@app.get("/", tags=["Health"])
def home() -> dict[str, str]:
    return {"message": "API is running", "version": settings.app_version}


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/health/ready", tags=["Health"])
def ready(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    return {"status": "ready"}