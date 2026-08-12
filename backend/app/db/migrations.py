"""Database migration manager for dk_travel."""
import logging
from alembic import command
from alembic.config import Config
from pathlib import Path

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations using Alembic."""

    def __init__(self, db_url: str):
        self.alembic_cfg = Config()
        self.alembic_cfg.set_main_option(
            "script_location", str(Path(__file__).parent / "alembic")
        )
        self.alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    def upgrade(self, revision: str = "head"):
        """Run migrations up to the specified revision."""
        logger.info(f"Running upgrade to {revision}")
        command.upgrade(self.alembic_cfg, revision)

    def downgrade(self, revision: str = "-1"):
        """Rollback migrations."""
        logger.info(f"Running downgrade to {revision}")
        command.downgrade(self.alembic_cfg, revision)

    def current(self):
        """Show current migration revision."""
        command.current(self.alembic_cfg)

    def history(self):
        """Show migration history."""
        command.history(self.alembic_cfg)

    def generate(self, message: str):
        """Auto-generate a new migration."""
        logger.info(f"Generating migration: {message}")
        command.revision(
            self.alembic_cfg,
            message=message,
            autogenerate=True,
        )
