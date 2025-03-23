import mysql.connector
import json

# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "@ditya000",
    "database": "user_message_info"
}


class Database:
    def __init__(self):
        """Initialize database connection."""
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor()

    def insert_data(self, message_id, padding, operation_values):
        """Insert encryption data into the database."""
        query = """
        INSERT INTO encryption_data (message_id, padding, operation_values)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE padding = VALUES(padding), operation_values = VALUES(operation_values)
        """
        self.cursor.execute(query, (message_id, json.dumps(padding), json.dumps(operation_values)))
        self.db.commit()

    def retrieve_data(self, message_id):
        """Retrieve encryption data using message_id."""
        query = "SELECT padding, operation_values FROM encryption_data WHERE message_id = %s"
        self.cursor.execute(query, (message_id,))
        result = self.cursor.fetchone()

        if result:
            padding = json.loads(result[0])
            operation_values = json.loads(result[1])
            return padding, operation_values
        return None, None

    def close_connection(self):
        """Close the database connection."""
        self.cursor.close()
        self.db.close()
