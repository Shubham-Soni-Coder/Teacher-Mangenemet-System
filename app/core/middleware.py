from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings


def setup_middleware(app):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        same_site="lax",
        https_only=False,  # True in production
    )
