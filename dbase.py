import mysql.connector  # Or your preferred MySQL driver

def create_player_table(connection):
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE player (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        position VARCHAR(50) NOT NULL,
        image_url VARCHAR(255) NOT NULL,
        is_potm BOOLEAN DEFAULT FALSE
    );
    """

    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Player table created successfully.")
    except mysql.connector.Error as err:
        if err.errno == 1050:  # Table already exists
            print("Player table already exists.")
        else:
            print(f"Error creating table: {err}")
            raise  # Re-raise the exception for handling elsewhere
    finally:
        cursor.close()

# Example usage (replace with your database credentials)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="befa"
)

create_player_table(mydb)

mydb.close()