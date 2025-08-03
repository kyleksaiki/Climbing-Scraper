import mysql.connector
from mysql.connector import errorcode
import argparse

# Global database configuration, edit these!
# Also view if __name__ == '__main__': to decide whether you want to insert demo data beforehand
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = '1234'
DB_NAME = 'climbing'

def get_connection(database: str = None):
    """
    Establish a connection to the MySQL server using global constants.
    If database is provided, connects directly to that database.
    """
    config = {
        'host': DB_HOST,
        'user': DB_USER,
        'password': DB_PASS,
    }
    if database:
        config['database'] = database
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid credentials")
        else:
            print(f"Error: {err}")
        raise


def create_schema(conn):
    """
    Create the 'climbing' database and all required tables.
    Drops the database if it already exists.
    """
    statements = [
        "DROP DATABASE IF EXISTS {0};".format(DB_NAME),
        "CREATE DATABASE {0};".format(DB_NAME),
        "USE {0};".format(DB_NAME),
        # climb_area table
        (
            "CREATE TABLE climb_area ("
            " AID INT UNSIGNED,"
            " area_name VARCHAR(50),"
            " latitude FLOAT,"
            " longitude FLOAT,"
            " mt_proj_link VARCHAR(200),"
            " state VARCHAR(50),"
            " PRIMARY KEY (AID)"
            ");"
        ),
        # area_descriptions table
        (
            "CREATE TABLE area_descriptions ("
            " AID INT UNSIGNED NOT NULL,"
            " text_data VARCHAR(5000),"
            " FOREIGN KEY (AID) REFERENCES climb_area(AID)"
            ");"
        ),
        # area_comments table
        (
            "CREATE TABLE area_comments ("
            " AID INT UNSIGNED NOT NULL,"
            " text_data VARCHAR(5000),"
            " FOREIGN KEY (AID) REFERENCES climb_area(AID)"
            ");"
        ),
        # climb table
        (
            "CREATE TABLE climb ("
            " CID INT UNSIGNED NOT NULL AUTO_INCREMENT,"
            " AID INT UNSIGNED NOT NULL,"
            " climb_name VARCHAR(200),"
            " climb_type VARCHAR(20),"
            " mp_stars INT UNSIGNED,"
            " num_mp_star INT UNSIGNED,"
            " mp_grade VARCHAR(5),"
            " vl_ascents INT UNSIGNED,"
            " vl_recommends INT UNSIGNED,"
            " os_rate FLOAT,"
            " vl_grade VARCHAR(5),"
            " redpoint INT UNSIGNED,"
            " flash INT UNSIGNED,"
            " go INT UNSIGNED,"
            " top_rope INT UNSIGNED,"
            " onsight INT UNSIGNED,"
            " PRIMARY KEY (CID),"
            " FOREIGN KEY (AID) REFERENCES climb_area(AID)"
            ") ENGINE=InnoDB;"
        ),
        # climb_descriptions table
        (
            "CREATE TABLE climb_descriptions ("
            " CID INT UNSIGNED NOT NULL,"
            " text_data VARCHAR(5000),"
            " FOREIGN KEY (CID) REFERENCES climb(CID) ON DELETE CASCADE"
            ");"
        ),
        # climb_comments table
        (
            "CREATE TABLE climb_comments ("
            " CID INT UNSIGNED NOT NULL,"
            " text_data VARCHAR(5000),"
            " site VARCHAR(500),"
            " FOREIGN KEY (CID) REFERENCES climb(CID) ON DELETE CASCADE"
            ");"
        ),
        # photos table
        (
            "CREATE TABLE photos ("
            " CID INT UNSIGNED NOT NULL,"
            " link VARCHAR(500),"
            " FOREIGN KEY (CID) REFERENCES climb(CID) ON DELETE CASCADE"
            ");"
        ),
    ]

    cursor = conn.cursor()
    for stmt in statements:
        try:
            cursor.execute(stmt)
            print(f"Executed: {stmt.split()[0]}")
        except mysql.connector.Error as err:
            print(f"Failed to execute: {stmt[:30]}... Error: {err}")
            cursor.close()
            raise
    conn.commit()
    cursor.close()
    print("Schema created successfully.")


def seed_data(conn):
    """
    Insert initial data into climb_area table.
    """
    insert_stmt = (
        "INSERT INTO climb_area "
        "(AID, area_name, latitude, longitude, mt_proj_link, state) VALUES (%s, %s, %s, %s, %s, %s)"
    )
    data = [
        (1, 'Big Columbia Boulder', 37.7417, -119.6037,
         'https://www.mountainproject.com/area/109861444/big-columbia-boulder', 'California'),
        (2, 'Manure Pile Buttress', 37.73059, -119.619,
         'https://www.mountainproject.com/area/105833498/manure-pile-buttress-aka-ranger-rock', 'California'),
        (3, 'Bridalveil Boulder', 37.71552, -119.65022,
         'https://www.mountainproject.com/area/112517146/bridalveil-boulder', 'California'),
        (4, 'Sentinel Boulder', 37.73389, -119.6018,
         'https://www.mountainproject.com/area/110670017/b-1-boulder', 'California'),
    ]
    cursor = conn.cursor()
    try:
        cursor.executemany(insert_stmt, data)
        conn.commit()
        print(f"Inserted {cursor.rowcount} rows into climb_area.")
    except mysql.connector.Error as err:
        print(f"Failed to insert seed data: {err}")
        conn.rollback()
        raise
    finally:
        cursor.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create climbing database schema and optionally seed initial data.'
    )
    parser.add_argument('--seed', action='store_true',
                        help='Seed the climb_area table with initial data')
    args = parser.parse_args()

    # Connect without specifying a database to create schema
    conn = get_connection()
    create_schema(conn)
    conn.close()

    #Uncomment to add demo data for testing
    # Connect to the newly created database to insert seed data
   # conn = get_connection(DB_NAME)
    #seed_data(conn)
    #conn.close()
