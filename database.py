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

    def insert_data(self, message_id, hex_data, padding, operation_values):
        """Insert encryption data into the database."""
        query = """
        INSERT INTO encryption_data (message_id, hex_data, padding, operation_values)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE hex_data = VALUES(hex_data), padding = VALUES(padding), operation_values = VALUES(operation_values)
        """
        self.cursor.execute(query, (message_id, json.dumps(hex_data), json.dumps(padding), json.dumps(operation_values)))
        self.db.commit()

    def retrieve_data(self, message_id):
        """Retrieve encryption data using message_id."""
        query = "SELECT hex_data, padding, operation_values FROM encryption_data WHERE message_id = %s"
        self.cursor.execute(query, (message_id,))
        result = self.cursor.fetchone()

        if result:
            hex_data = json.loads(result[0])
            padding = json.loads(result[1])
            operation_values = json.loads(result[2])
            return hex_data, padding, operation_values
        return None, None, None

    def close_connection(self):
        """Close the database connection."""
        self.cursor.close()
        self.db.close()
