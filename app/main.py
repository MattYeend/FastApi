from fastapi import FastAPI

from app.api.routes import products, users
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="User and product management API",
    debug=settings.debug,
)


app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def home():
    return {"message": "API is running", "version": settings.app_version}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
