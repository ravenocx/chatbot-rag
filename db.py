import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def db_connection() :
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn

def get_all_products(db):
    cursor= db.cursor()
    cursor.execute("""
        SELECT 
        p.*, 
        c.name AS category_name,
        sc.name AS sub_category_name,
        b.name AS brand_name,
        FROM products p
        JOIN categories c ON p.category_id = c.id
        JOIN categories sc ON p.sub_category_id = sc.id
        JOIN brands b ON p.brand_id = b.id
        WHERE p.deleted_at IS NULL AND p.status != 2
    """)
    
    rows = cursor.fetchall()
    return rows