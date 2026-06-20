from functools import wraps

from flask import redirect, render_template, request, url_for
from flask_login import current_user


def _redirect_to_login():
    return redirect(url_for("public.login", next=request.path))


def _render_forbidden():
    return render_template("errors/403.html"), 403


def role_required(role_name: str):
    """Return a decorator that grants access only to users with the given role.

    If the user is not authenticated, this behaves like login_required and redirects
    the client to the login page. If the user is authenticated but does not have
    the required role, it returns a 403 Forbidden response.
    """

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return _redirect_to_login()

            if not current_user.has_role(role_name):
                return _render_forbidden()

            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def permission_required(permission_name: str):
    """Return a decorator that grants access only to users with the given permission.

    If the user is not authenticated, this behaves like login_required and redirects
    the client to the login page. If the user is authenticated but does not have
    the required permission, it returns a 403 Forbidden response.
    """

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return _redirect_to_login()

            if not current_user.has_permission(permission_name):
                return _render_forbidden()

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
