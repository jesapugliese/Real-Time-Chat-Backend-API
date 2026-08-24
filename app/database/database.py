from loguru import logger
import os
import psycopg


class Database:
    @staticmethod
    def get_connection() -> psycopg.Connection:
        """Establishes and returns a new database connection."""

        return psycopg.connect(
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT"),
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
        )

    @staticmethod
    def init_db():
        """Initializes the database by creating necessary tables."""

        logger.info("Initializing database.")
        Database.__init_channels_table()
        Database.__init_messages_table()
        logger.info("Database initialized successfully.")

    @staticmethod
    def __init_channels_table():
        logger.info("Initializing channels table.")

        db_conn = Database.get_connection()

        try:
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

            db_conn.commit()
        finally:
            db_conn.close()

    @staticmethod
    def __init_messages_table():
        logger.info("Initializing messages table.")

        db_conn = Database.get_connection()

        try:
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

            db_conn.commit()
        finally:
            db_conn.close()
