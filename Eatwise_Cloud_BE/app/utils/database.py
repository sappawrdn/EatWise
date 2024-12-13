from pymysql import connect

def get_db_connection():
    return connect(
        host="34.101.149.230",
        user="root",
        password="eatwise-sql",
        database="eatwise-db-data",
    )

def execute_query(conn, query, args=None):
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        conn.commit()
