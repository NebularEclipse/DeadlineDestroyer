import mysql.connector
from mysql.connector import errorcode, Error

class DBManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
        # Try connecting to MySQL and checking/creating the database
        self.connect_to_mysql()

    def connect_to_mysql(self):
        try:
            # Connect to MySQL without specifying a database
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor()

            # Check if the database exists
            cursor.execute(f"SHOW DATABASES LIKE '{self.database}'")
            result = cursor.fetchone()

            # If the database doesn't exist, create it
            if not result:
                print(f"Database '{self.database}' does not exist. Creating it...")
                cursor.execute(f"CREATE DATABASE {self.database}")
                print(f"Database '{self.database}' created successfully.")

            # Now, connect to the newly created or existing database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to database '{self.database}'.")

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your username or password.")
            else:
                print(err)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()

    def create_table(self, table_name, schema):
        # Create a table with the given schema
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        self.cursor.execute(query)
        self.connection.commit()
        print(f"Table {table_name} created successfully.")

    def insert_data(self, table_name, columns, values):
        # Insert data into a table
        cols = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.connection.commit()
        print("Data inserted successfully.")

    def fetch_data(self, table_name):
        # Retrieve all rows from the table
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def update_data(self, table_name, update_column, new_value, condition):
        # Update data based on a condition
        query = f"UPDATE {table_name} SET {update_column} = %s WHERE {condition}"
        self.cursor.execute(query, (new_value,))
        self.connection.commit()
        print(f"Data updated in {table_name} where {condition}.")

    def delete_data(self, table_name, condition):
        # Delete data based on a condition
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query)
        self.connection.commit()
        print(f"Data deleted from {table_name} where {condition}.")

    def query(self, query, params=None):
        """ Execute a SELECT SQL query and return the results. """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()  # Fetch all results
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def close(self):
        # Close the connection
        self.cursor.close()
        self.connection.close()
        print("Database connection closed.")