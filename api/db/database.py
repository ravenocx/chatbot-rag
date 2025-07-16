import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def db_connection() :
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )
    return conn

def get_user(db, email:str):
    cursor= db.cursor(dictionary=True)
    cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    return user

def get_admin(db, email:str):
    cursor= db.cursor(dictionary=True)
    cursor.execute("SELECT id, email, password FROM admins WHERE email = %s", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    return user
