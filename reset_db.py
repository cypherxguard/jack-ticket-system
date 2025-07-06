#!/usr/bin/env python3
"""
Reset database and recreate all tables
"""

from app import app, db
from auth.models import User
from auth.utils import hash_password

def reset_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            password_hash=hash_password('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        
        print("Verifying user creation...")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} (role: {user.role})")
        
        print("Database reset completed successfully!")

if __name__ == "__main__":
    reset_database() 