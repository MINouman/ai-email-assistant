import sys
from app.database import engine, Base, SessionLocal
from app.models.models import User, Email

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database Tables created")

def drop_tables():
    response = input("Are you sure to delete tables? (yes/no): ")
    if response.lower() == 'yes':
        Base.metadata.drop_all(bind=engine)
        print("table deleted")
    else:
        print("Operation cancelled")

def show_tables():
    db = SessionLocal()
    try:
        print("\nDatabase Info:")
        print("-"*30)

        user_count = db.query(User).count()
        email_count = db.query(Email).count()

        print(f"Users: {user_count}")
        print(f"Emails: {email_count}")
        print("-"*40)

    finally:
        db.close()

def show_users():
    """Display all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\nUsers:")
        print("-" * 60)
        for user in users:
            print(f"ID: {user.id} | Email: {user.email} | Name: {user.full_name}")
        print("-" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    commands = {
        "create": create_tables,
        "drop": drop_tables,
        "stats": show_tables,
        "users": show_users,
    }
    
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("Usage: python manage_db.py [command]")
        print("\nAvailable commands:")
        print("  create  - Create database tables")
        print("  drop    - Drop all tables")
        print("  stats   - Show table statistics")
        print("  users   - List all users")
        sys.exit(1)
    
    commands[sys.argv[1]]()