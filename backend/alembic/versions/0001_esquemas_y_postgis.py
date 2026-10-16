"""Extensión PostGIS y esquemas core, private, analytics y audit.

Revision ID: 0001
Revises:
Create Date: 2026-10-16
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMAS = ("core", "private", "analytics", "audit")


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    for esquema in ESQUEMAS:
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {esquema}")


def downgrade() -> None:
    for esquema in reversed(ESQUEMAS):
        op.execute(f"DROP SCHEMA IF EXISTS {esquema} CASCADE")
