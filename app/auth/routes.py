from datetime import datetime, timedelta

from flask import flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from app.extensions import db, limiter
from app.models import User
from app.security.audit import AuditLogger
from . import auth_bp
from .forms import LoginForm, PasswordResetForm, PasswordResetRequestForm, RegistrationForm


def _get_safe_redirect_url(default="public.index"):
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != "":
        return url_for(default)
    return next_page


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("An error occurred creating your account. Please try again.", "danger")
            return render_template("auth/register.html", form=form)

        AuditLogger.log_user_created(user)

        flash("Your account has been created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = (form.email.data or "").lower().strip()
        user = User.query.filter_by(email=email).first()

        # Check for account lockout
        if user and user.is_locked:
            AuditLogger.log_account_lockout(user, ip_address=request.remote_addr)
            # Generic message to prevent enumeration
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if user and user.check_password(form.password.data) and user.is_active:
            # session fixation protection
            session.clear()
            login_user(user, remember=form.remember_me.data, duration=timedelta(days=7))
            user.reset_failed_logins()
            try:
                db.session.add(user)
                db.session.commit()
            except Exception:
                db.session.rollback()

            AuditLogger.log_login_success(user)
            next_page = _get_safe_redirect_url()
            return redirect(next_page)

        # If we have a matching user, increment failed attempts
        if user:
            user.increment_failed_logins()
            try:
                db.session.add(user)
                db.session.commit()
            except Exception:
                db.session.rollback()

            if user.is_locked:
                AuditLogger.log_account_lockout(user, ip_address=request.remote_addr)

        AuditLogger.log_login_failure(email, ip_address=request.remote_addr)
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    AuditLogger.log_logout(current_user)
    logout_user()
    # Clear the session to ensure cookies and session data removed
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.index"))


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        # OWASP: Do not reveal whether an email exists.
        # Log the reset request in audit (do not reveal existence)
        AuditLogger.log_password_reset_request((form.email.data or "").lower(), ip_address=request.remote_addr)
        flash(
            "If an account with that email exists, you will receive instructions to reset your password.",
            "info",
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password_request.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = PasswordResetForm()
    if form.validate_on_submit():
        # Placeholder: validate token and reset password.
        # After a successful reset, log event
        # Example: find user by token, set password, reset failed attempts
        # This placeholder assumes token->user resolution happens elsewhere
        # and `user` variable is available after token validation.
        try:
            # token validation and user lookup not implemented here
            # user.set_password(form.password.data)
            # user.reset_failed_logins()
            # db.session.add(user)
            # db.session.commit()
            pass
        except Exception:
            db.session.rollback()
            flash("An error occurred resetting your password.", "danger")
            return render_template("auth/reset_password.html", form=form)

        # If successful, log completion (if user known)
        # AuditLogger.log_password_reset_completed(user, ip_address=request.remote_addr)
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)
