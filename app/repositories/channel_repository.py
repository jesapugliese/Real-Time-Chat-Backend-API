from app.database.database import Database
from app.models.channel import Channel


class ChannelRepository:
    @staticmethod
    def create(channel_name: str) -> Channel:
        """
        Creates a new channel with the given name and returns the created
        Channel object.
        """

        db_conn = Database.get_connection()

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO channels (name) 
                    VALUES (%s) 
                    RETURNING id, name, createdAt
                    """,
                    (channel_name,),
                )

                channel = cursor.fetchone()
                db_conn.commit()

                return Channel(id=channel[0], name=channel[1], createdAt=channel[2])
        finally:
            db_conn.close()

    @staticmethod
    def find_by_name_ci(channel_name: str) -> Channel | None:
        """
        Finds a channel by name (case-insensitive) and returns the Channel
        object if found, otherwise None.
        """

        db_conn = Database.get_connection()

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, createdAt 
                    FROM channels 
                    WHERE LOWER(name) = LOWER(%s)
                    """,
                    (channel_name,),
                )

                channel = cursor.fetchone()

                return (
                    Channel(id=channel[0], name=channel[1], createdAt=channel[2])
                    if channel
                    else None
                )
        finally:
            db_conn.close()

    @staticmethod
    def get_all() -> list[Channel]:
        """
        Retrieves all channels from the database and returns a list of
        Channel objects, ordered by creation date in ascending order.
        """

        db_conn = Database.get_connection()

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, createdAt 
                    FROM channels 
                    ORDER BY createdAt ASC
                    """
                )

                channels = cursor.fetchall()

                return [
                    Channel(id=channel[0], name=channel[1], createdAt=channel[2])
                    for channel in channels
                ]
        finally:
            db_conn.close()

    @staticmethod
    def exists_by_id(channel_id: int) -> bool:
        """
        Checks if a channel with the given ID exists in the database.
        Returns True if it exists, otherwise False.
        """

        db_conn = Database.get_connection()

        try:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 1 
                    FROM channels 
                    WHERE id = %s
                    """,
                    (channel_id,),
                )

                return cursor.fetchone() is not None
        finally:
            db_conn.close()
