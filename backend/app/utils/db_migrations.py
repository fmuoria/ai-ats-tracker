"""
Database migration helper for adding new columns without Alembic
This is a simple migration helper for MVP - for production use Alembic
"""
from sqlalchemy import text, inspect
from ..models.database import engine
import logging

logger = logging.getLogger(__name__)


def add_column_if_not_exists(table_name: str, column_name: str, column_definition: str):
    """
    Add a column to a table if it doesn't exist
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to add
        column_definition: SQL definition of the column (e.g., "VARCHAR(255) DEFAULT NULL")
    """
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        if column_name not in columns:
            with engine.begin() as conn:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                conn.execute(text(sql))
                logger.info(f"Added column {column_name} to {table_name}")
                return True
        else:
            logger.info(f"Column {column_name} already exists in {table_name}")
            return False
    except Exception as e:
        logger.error(f"Error adding column {column_name} to {table_name}: {str(e)}")
        return False


def run_migrations():
    """
    Run all pending migrations
    This should be called on application startup
    """
    logger.info("Running database migrations...")
    
    # Add new columns to candidates table
    migrations = [
        ("candidates", "resume_embedding", "JSON"),
        ("candidates", "jd_id", "INTEGER"),
        ("candidates", "jd_match_score", "FLOAT"),
        ("candidates", "matched_skills", "JSON"),
        ("candidates", "missing_skills", "JSON"),
        ("candidates", "final_score", "FLOAT"),
    ]
    
    for table, column, definition in migrations:
        add_column_if_not_exists(table, column, definition)
    
    logger.info("Database migrations completed")


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {str(e)}")
        return False
