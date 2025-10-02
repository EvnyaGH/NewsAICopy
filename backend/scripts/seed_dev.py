from __future__ import annotations

"""
Dev seeding script: creates base roles/permissions and a couple of users.

Usage:
  uv run python scripts/seed_dev.py


"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.shared.security import hash_password
from app.shared.config import settings
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.permission import Permission, RolePermission


def get_or_create_role(db: Session, name: str, description: Optional[str] = None) -> Role:
    obj = db.query(Role).filter_by(name=name).one_or_none()
    if obj:
        return obj
    obj = Role(name=name, description=description)
    db.add(obj)
    db.flush()
    return obj


def get_or_create_permission(db: Session, name: str, resource: Optional[str] = None,
                             action: Optional[str] = None) -> Permission:
    obj = db.query(Permission).filter_by(name=name).one_or_none()
    if obj:
        return obj
    obj = Permission(name=name, resource=resource, action=action)
    db.add(obj)
    db.flush()
    return obj


def ensure_role_permission(db: Session, role: Role, perm: Permission) -> None:
    link = (
        db.query(RolePermission)
        .filter(RolePermission.role_id == role.id, RolePermission.permission_id == perm.id)
        .one_or_none()
    )
    if not link:
        db.add(RolePermission(role_id=role.id, permission_id=perm.id))


def get_or_create_user(db: Session, email: str, password: str, **kwargs) -> User:
    u = db.query(User).filter_by(email=email).one_or_none()
    if u:
        return u
    u = User(email=email, password_hash=hash_password(password), **kwargs)
    db.add(u)
    db.flush()
    return u


def ensure_user_role(db: Session, user: User, role: Role) -> None:
    link = (
        db.query(UserRole)
        .filter(UserRole.user_id == user.id, UserRole.role_id == role.id)
        .one_or_none()
    )
    if not link:
        db.add(UserRole(user_id=user.id, role_id=role.id))


def main() -> None:
    # Create a standalone engine/session using .env-configured URL
    db_url = settings.database_url
    if db_url.startswith("sqlite"):
        raise SystemExit(
            "Seed aborted: DATABASE_URL points to SQLite. Set a Postgres DATABASE_URL in .env (e.g., postgresql+psycopg://user:pass@host:5432/db)."
        )
    engine = create_engine(db_url, future=True)
    LocalSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    db = LocalSession()
    try:
        # Roles
        user_role = get_or_create_role(db, "reader", "Default user role")
        author_role = get_or_create_role(db, "author", "Author user role")
        admin_role = get_or_create_role(db, "admin", "Administrator role")

        # Permissions (example baseline)
        me_read = get_or_create_permission(db, "me.read", resource="me", action="read")

        # Link permissions to roles
        ensure_role_permission(db, user_role, me_read)
        ensure_role_permission(db, author_role, me_read)
        ensure_role_permission(db, admin_role, me_read)

        # Users
        dev_user = get_or_create_user(db, "user@example.com", "password", display_name="Dev User")
        dev_admin = get_or_create_user(db, "admin@example.com", "password", display_name="Dev Admin")

        # Assign roles
        ensure_user_role(db, dev_user, user_role)
        ensure_user_role(db, dev_admin, admin_role)

        db.commit()
        print("Seed complete. Users: user@example.com / admin@example.com (password: password)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
