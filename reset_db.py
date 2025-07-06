#!/usr/bin/env python3
"""
Reset database with new ticket_id field using SQLAlchemy
"""

import os
from app import app, db
from auth.models import User
from auth.utils import hash_password

def reset_database():
    """Reset the database with new schema including ticket_id"""
    
    with app.app_context():
        # Remove existing database files
        db_files = ['ticket_system.db', 'instance/ticket_system.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"✓ Removed {db_file}")
        
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        
        # Create all tables using SQLAlchemy
        print("Creating all tables...")
        db.create_all()
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if not existing_admin:
            # Create admin user
            print("Creating admin user...")
            admin_user = User(
                username='admin',
                password_hash=hash_password('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")
        else:
            print("✓ Admin user already exists")
        
        print("✓ Database created with new schema")
        print("\n🎉 Database reset complete! You can now use the application.")

if __name__ == "__main__":
    print("Resetting database with new ticket_id field...")
    reset_database() 