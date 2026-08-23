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

        Database.__init_channels_table()

    @staticmethod
    def __init_channels_table():
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

                    CREATE UNIQUE INDEX channels_name_lower_unique
                    ON channels (LOWER(name));
                    """
                )

            db_conn.commit()
        finally:
            db_conn.close()
