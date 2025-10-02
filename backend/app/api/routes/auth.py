from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status, Request

from app.exceptions.exceptions import InvalidCredentialsError, EmailVerificationNotVerified, UserDoesNotExist
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, VerifyEmailRequest, ResendEmailVerificationRequest
from app.services.session_service import get_session_service, SessionService
from app.services.user_service import UserService, get_user_service
from app.shared.config import settings
from app.shared.security import verify_password, hash_password

router = APIRouter()


@router.post(
	"/login",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Login and set session cookie",
)
async def login(
		payload: LoginRequest,
		response: Response,
		user_service: UserService = Depends(get_user_service),
		session_service: SessionService = Depends(get_session_service),
):
	"""Authenticates a user and establishes a session.

	On successful authentication, an HttpOnly, Secure cookie is set with the
	session ID (`sid`). The response has no body.
	"""
	user: User | None = user_service.find_by_email(payload.email.__str__())
	if not user:
		raise UserDoesNotExist("user does not exist")

	if not verify_password(payload.password, user.password_hash.__str__()):
		raise InvalidCredentialsError("invalid credentials")

	if user.email_verified_at is None:
		raise EmailVerificationNotVerified("user email not verified")

	roles = []
	for role in user.roles:
		roles.append(role.name)

	sid, ttl, _ = await session_service.create_session(user_id=str(user.id), roles=roles)

	cookie_params = {
		"key": settings.session_cookie_name,
		"value": sid,
		"httponly": True,
		"secure": settings.session_cookie_secure,
		"samesite": settings.session_cookie_samesite,
		"path": settings.session_cookie_path,
		"max_age": ttl,
	}
	if settings.session_cookie_domain:
		cookie_params["domain"] = settings.session_cookie_domain

	response.set_cookie(**cookie_params)
	return


@router.post(
	"/logout",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Logout and clear session cookie",
)
async def logout(
		request: Request,
		response: Response,
		session_service: SessionService = Depends(get_session_service),
):
	"""Deletes the user session and clears the session cookie."""
	sid = request.cookies.get(settings.session_cookie_name)
	if sid:
		await session_service.delete_session(sid)

	response.delete_cookie(
		key=settings.session_cookie_name,
		domain=settings.session_cookie_domain,
		path=settings.session_cookie_path,
	)
	return


@router.post(
	"/register",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Register new user",
)
async def register(
		request: RegisterRequest,
		user_service: UserService = Depends(get_user_service),
):
	"""Registers a new user."""

	user = User(
		email=request.email.__str__(),
		display_name=request.display_name,
		first_name=request.first_name,
		last_name=request.last_name,
		password_hash=hash_password(request.password),
		email_verified_at=None,
	)

	roles = request.roles or ["reader"]
	await user_service.register(user, roles=roles)

	return


@router.post(
	"/verify-email",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Verify email",
)
async def verify_email(
		request: VerifyEmailRequest,
		user_service: UserService = Depends(get_user_service),
):
	"""Verifies an email address."""
	await user_service.verify_email(token=request.token)
	return


@router.post(
	"/resend-email-verification",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Resend email verification",
)
async def resend_email_verification(
		request: ResendEmailVerificationRequest,
		user_service: UserService = Depends(get_user_service),
):
	"""Resends an email verification email."""

	user: User | None = user_service.find_by_email(request.email.__str__())
	if not user or not verify_password(request.password, user.password_hash.__str__()):
		raise InvalidCredentialsError("Invalid credentials")

	await user_service.send_verification_email(user.email.__str__())
	return
