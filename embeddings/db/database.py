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

def get_all_products(db):
    cursor= db.cursor(dictionary=True)
    cursor.execute("""\
        SELECT 
        p.*, 
        c.name AS category_name,
        sc.name AS sub_category_name,
        b.name AS brand_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id AND p.category_id IS NOT NULL
        LEFT JOIN categories sc ON p.sub_category_id = sc.id AND p.sub_category_id IS NOT NULL
        LEFT JOIN brands b ON p.brand_id = b.id AND p.brand_id IS NOT NULL
        WHERE p.deleted_at IS NULL AND p.status != 2
    """)
    
    rows = cursor.fetchall()
    return rows

def get_all_attributes(db):
    cursor= db.cursor(dictionary=True)
    cursor.execute("""\
        SELECT 
        id, name 
        FROM attributes
        WHERE status = 1
    """)
    
    rows = cursor.fetchall()
    attributes = {row["id"]: row["name"] for row in rows}
    return attributes
