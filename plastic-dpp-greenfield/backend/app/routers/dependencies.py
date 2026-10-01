import logging

from fastapi import Header

from app.models.account import Role, UserRoleAccount
from app.services.errors import UnauthorizedRoleError

logger = logging.getLogger("plastic_dpp.audit")


def get_current_account(
    x_role: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> UserRoleAccount:
    """Mock-auth: resolve the caller from X-Role / X-User-Id headers (research.md).

    Real authentication is a future-phase concern; this satisfies NFR-003 for the MVP.
    """
    if not x_role or not x_user_id:
        raise UnauthorizedRoleError("Missing X-Role or X-User-Id header")
    try:
        role = Role(x_role)
    except ValueError:
        raise UnauthorizedRoleError(f"Unknown role: {x_role}")
    return UserRoleAccount(user_id=x_user_id, role=role)


def log_action(account: UserRoleAccount, action: str, target: str) -> None:
    """Audit log for lifecycle-changing actions (NFR-007)."""
    logger.info(
        "action=%s actor=%s role=%s target=%s",
        action,
        account.user_id,
        account.role.value,
        target,
    )

