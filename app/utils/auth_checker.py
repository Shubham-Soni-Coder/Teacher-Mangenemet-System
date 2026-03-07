from fastapi.responses import RedirectResponse
from fastapi import status


def redirect_by_user(role: str):
    if not role:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    role_key = role.lower()
    if role_key == "teacher":
        return RedirectResponse(
            url="/teacher/dashboard", status_code=status.HTTP_303_SEE_OTHER
        )
    elif role_key == "student":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    elif role_key == "admin":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    # Fallback for unknown roles
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
