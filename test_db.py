#!/usr/bin/env python3
"""
Test database creation and User model
"""

from app import app, db
from auth.models import User
from auth.utils import hash_password

def test_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Creating test admin user...")
        admin_user = User(
            username='admin',
            password_hash=hash_password('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        
        print("Querying users...")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} (role: {user.role})")
        
        print("Database test completed successfully!")

if __name__ == "__main__":
    test_database() 