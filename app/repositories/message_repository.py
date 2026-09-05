from app.database.database import Database
from app.models.message import Message


class MessageRepository:
    @staticmethod
    def create(channel_id: int, author_id: int, content: str) -> Message:
        """
        Creates a new message in the specified channel with the given author
        and content, and returns the created Message object.
        """

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO messages (channelId, authorId, content) 
                    VALUES (%s, %s, %s) 
                    RETURNING id, channelId, authorId, content, createdAt, editedAt
                    """,
                    (channel_id, author_id, content),
                )

                message = cursor.fetchone()

                return Message(
                    id=message[0],
                    channelId=message[1],
                    authorId=message[2],
                    content=message[3],
                    createdAt=message[4],
                    editedAt=message[5],
                )

    @staticmethod
    def find_by_id(message_id: int) -> Message | None:
        """
        Finds a message by its ID and returns the Message object if found,
        otherwise None.
        """

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, channelId, authorId, content, createdAt, editedAt 
                    FROM messages 
                    WHERE id = %s
                    """,
                    (message_id,),
                )

                message = cursor.fetchone()

                return (
                    Message(
                        id=message[0],
                        channelId=message[1],
                        authorId=message[2],
                        content=message[3],
                        createdAt=message[4],
                        editedAt=message[5],
                    )
                    if message
                    else None
                )

    @staticmethod
    def update(message_id: int, new_content: str) -> Message:
        """
        Updates the content of a message with the given ID and returns the
        updated Message object.
        """

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE messages 
                    SET content = %s, editedAt = CURRENT_TIMESTAMP 
                    WHERE id = %s 
                    RETURNING id, channelId, authorId, content, createdAt, editedAt
                    """,
                    (new_content, message_id),
                )

                message = cursor.fetchone()

                return Message(
                    id=message[0],
                    channelId=message[1],
                    authorId=message[2],
                    content=message[3],
                    createdAt=message[4],
                    editedAt=message[5],
                )

    @staticmethod
    def find_by_channel_id(channel_id: int) -> list[Message]:
        """
        Retrieves all messages in the specified channel and returns a list of
        Message objects.
        """

        with Database.pool.connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, channelId, authorId, content, createdAt, editedAt 
                    FROM messages 
                    WHERE channelId = %s
                    ORDER BY createdAt ASC, id ASC
                    """,
                    (channel_id,),
                )

                messages = cursor.fetchall()

                return [
                    Message(
                        id=message[0],
                        channelId=message[1],
                        authorId=message[2],
                        content=message[3],
                        createdAt=message[4],
                        editedAt=message[5],
                    )
                    for message in messages
                ]
