from loguru import logger
import os
from psycopg_pool import ConnectionPool


# TODO: Close the connection pool when the application shuts down
class Database:
    pool: ConnectionPool | None = None

    @staticmethod
    def init_db():
        """Initializes the database."""

        logger.info("Initializing database.")
        Database.__init_connection_pool()
        Database.__init_channels_table()
        Database.__init_messages_table()
        logger.info("Database initialized successfully.")

    @staticmethod
    def __init_connection_pool():
        logger.info("Initializing database connection pool.")

        try:
            Database.pool = ConnectionPool(
                conninfo=f"host={os.getenv('DATABASE_HOST')} "
                f"port={os.getenv('DATABASE_PORT')} "
                f"dbname={os.getenv('DATABASE_NAME')} "
                f"user={os.getenv('DATABASE_USER')} "
                f"password={os.getenv('DATABASE_PASSWORD')}",
                open=True,
            )

            Database.pool.wait()
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    @staticmethod
    def __init_channels_table():
        logger.info("Initializing channels table.")

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS channels (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        createdAt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE UNIQUE INDEX IF NOT EXISTS channels_name_lower_unique
                    ON channels (LOWER(name));
                    """
                )

    @staticmethod
    def __init_messages_table():
        logger.info("Initializing messages table.")

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        channelId SERIAL NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
                        authorId SERIAL NOT NULL,
                        content VARCHAR(2000) NOT NULL,
                        createdAt TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        editedAt TIMESTAMPTZ NULL
                    );
                    """
                )

    @staticmethod
    def close_pool():
        """Closes the database connection pool."""

        if Database.pool:
            logger.info("Closing database connection pool.")
            Database.pool.close()
            Database.pool = None
            logger.info("Database connection pool closed.")
