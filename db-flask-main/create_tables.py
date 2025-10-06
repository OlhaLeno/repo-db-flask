#!/usr/bin/env python3
"""
Скрипт для створення таблиць в базі даних
"""
from __init__ import create_app
from my_project.db_init import db
from sqlalchemy import text

def create_tables():
    app = create_app()
    
    with app.app_context():
        try:
            print("🔗 Підключення до бази даних...")
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Перевірити підключення
            result = db.session.execute(text('SELECT 1'))
            print("✅ Підключення до бази даних успішне!")
            
            # Створити таблиці
            print("📋 Створення таблиць...")
            db.create_all()
            print("✅ Таблиці створені успішно!")
            
            # Перевірити які таблиці створені
            result = db.session.execute(text('SHOW TABLES'))
            tables = result.fetchall()
            print(f"📊 Створено таблиць: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
                
        except Exception as e:
            print(f"❌ Помилка: {e}")
            return False
            
    return True

if __name__ == "__main__":
    create_tables()
