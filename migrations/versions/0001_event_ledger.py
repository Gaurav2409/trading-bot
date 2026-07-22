"""event ledger append-only store

Revision ID: 0001_event_ledger
Revises:
Create Date: 2026-07-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_event_ledger"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_log",
        sa.Column("event_id", sa.String(), primary_key=True),
        sa.Column("stream_id", sa.String(), nullable=False),
        sa.Column("stream_version", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("correlation_id", sa.String(), nullable=True),
        sa.Column("causation_id", sa.String(), nullable=True),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.UniqueConstraint("stream_id", "stream_version", name="uq_event_log_stream_version"),
    )
    op.create_index("ix_event_log_stream_id", "event_log", ["stream_id"])

    # Append-only enforcement: block UPDATE and DELETE regardless of role.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION trading_os_event_log_immutable()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'event_log is append-only: % is not permitted', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER event_log_no_update_delete
        BEFORE UPDATE OR DELETE ON event_log
        FOR EACH ROW EXECUTE FUNCTION trading_os_event_log_immutable();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS event_log_no_update_delete ON event_log;")
    op.execute("DROP FUNCTION IF EXISTS trading_os_event_log_immutable();")
    op.drop_index("ix_event_log_stream_id", table_name="event_log")
    op.drop_table("event_log")
