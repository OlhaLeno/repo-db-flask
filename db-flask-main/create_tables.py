#!/usr/bin/env python3
from __init__ import create_app
from my_project.db_init import db
from sqlalchemy import text

def create_tables():
    app = create_app()
    
    with app.app_context():
        try:
            print("Connecting to a database...")
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            result = db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            print("Creating tables...")
            db.create_all()
            print("Tables created successfully!")
            
            result = db.session.execute(text('SHOW TABLES'))
            tables = result.fetchall()
            print(f"Tables created: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
                
        except Exception as e:
            print(f"Error: {e}")
            return False
            
    return True

if __name__ == "__main__":
    create_tables()
