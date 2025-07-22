import psycopg2
import psycopg2.extras
import os

def db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )
    return conn

def get_user(db, email: str):
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    return user

def get_admin(db, email: str):
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, email, password FROM admins WHERE email = %s", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    return user

def create_user(db, name: str, email: str, phone_number: str, hashed_password: str):
    cursor = db.cursor()
    try:
        sql = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s) RETURNING id"
        cursor.execute(sql, (name, email, phone_number, hashed_password))
        new_user_id = cursor.fetchone()[0]
        db.commit()
        return new_user_id
    except Exception as e:
        db.rollback()
        print("debug:", str(e))
        return None
    finally:
        cursor.close()

def get_rag_configuration(db):
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM rag_configurations WHERE id = %s", (1,))
    
    rag_config = cursor.fetchone()
    cursor.close()
    return rag_config

def update_rag_configuration(db, data: dict):
    cursor = db.cursor()
    try:
        sql = """
        UPDATE rag_configurations 
        SET 
            main_instruction=%s,
            critical_instruction=%s,
            additional_guideline=%s,
            retriever_instruction=%s,
            top_k_retrieval=%s,
            updated_at=NOW()
        WHERE id = %s
        """

        cursor.execute(sql, (
            data["main_instruction"],
            data["critical_instruction"],
            data["additional_guideline"],
            data["retriever_instruction"],
            data["top_k_retrieval"],
            1
        ))

        db.commit()
    except Exception as e:
        db.rollback()
        print("debug :", str(e))
        return None
    finally:
        cursor.close()
        
    return get_rag_configuration(db)