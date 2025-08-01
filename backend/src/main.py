from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_csrf_protect.exceptions import CsrfProtectError

from src.api.main import api_router
from src.config import get_settings
from src.csrf import verify_csrf

app = FastAPI(dependencies=[Depends(verify_csrf)])


@app.exception_handler(CsrfProtectError)
async def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    response = JSONResponse(
        status_code=403,  # Always return 403 for CSRF failures
        content={
            "type": "Missing CSRF Token in header",
            "title": "Forbidden",
            "detail": str(exc),
            "instance": request.url.path,
            "method": request.method,
            "status": 403,
        },
    )

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    return response


settings = get_settings()


allowed_origins = [settings.home_location]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
