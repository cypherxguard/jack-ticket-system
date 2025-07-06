#!/usr/bin/env python3
"""
Test script for the authentication system
"""

from app import app, db, init_db
from auth.models import User
from auth.utils import hash_password, verify_password

def test_auth_system():
    with app.app_context():
        # Initialize database
        init_db()
        
        # Test password hashing
        password = "test123"
        hashed = hash_password(password)
        print(f"Password: {password}")
        print(f"Hashed: {hashed}")
        print(f"Verification: {verify_password(hashed, password)}")
        
        # Test user creation
        test_user = User(
            username="testuser",
            password_hash=hash_password("testpass"),
            role="user"
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Query users
        users = User.query.all()
        print(f"\nTotal users: {len(users)}")
        for user in users:
            print(f"- {user.username} ({user.role})")
        
        print("\nAuthentication system is working correctly!")

if __name__ == "__main__":
    test_auth_system() 