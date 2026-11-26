from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from app.api.routes import products, users
from app.core.config import settings
from app.core.exceptions import DomainError, domain_error_handler
from app.dependencies.auth import require_api_key

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="User and product management API",
    debug=settings.debug,
)

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
def home():
    return {"message": "API is running", "version": settings.app_version}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
