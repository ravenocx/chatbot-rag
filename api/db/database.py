import mysql.connector
import os

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

def create_user(db, name: str, email: str, phone_number:str, hashed_password:str):
    cursor = db.cursor()
    try:
        sql = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (name, email, phone_number, hashed_password))
        db.commit()
        new_user_id = cursor.lastrowid
        return new_user_id
    except Exception as e:
        print("[DEBUG] Create User Query error", str(e))
        db.rollback()
        return None
    finally:
        cursor.close()

def get_rag_configuration(db):
    cursor= db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rag_configurations WHERE id = %s", (1,))
    
    rag_config = cursor.fetchone()
    cursor.close()
    return rag_config