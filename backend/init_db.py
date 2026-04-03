# backend/init_db.py
from app.database.database import init_db, seed_questions

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding questions...")
    seed_questions()
    print("Database setup complete!")