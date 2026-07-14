#!/usr/bin/env python3
"""
04_seed_test_user.py — Create the shared test user if it doesn't exist.
Run with: /home/ubuntu/App-Web-Resser/venv/bin/python 04_seed_test_user.py
"""
import sys
import os

sys.path.insert(0, "/home/ubuntu/App-Web-Resser")
os.chdir("/home/ubuntu/App-Web-Resser")

from db import SessionLocal
from models.user import User
from models.enum import UserRoleEnum
from managers.auth import get_password_hash

TEST_EMAIL    = "test@resser.fr"
TEST_PASSWORD = "Resser2026!"
TEST_FNAME    = "Test"
TEST_LNAME    = "Resser"
TEST_POSTAL   = "75000"

db = SessionLocal()
try:
    existing = db.query(User).filter_by(email=TEST_EMAIL).first()
    if existing:
        print(f"[SKIP] User '{TEST_EMAIL}' already exists (id={existing.id}).")
    else:
        user = User(
            email           = TEST_EMAIL,
            hashed_password = get_password_hash(TEST_PASSWORD),
            first_name      = TEST_FNAME,
            last_name       = TEST_LNAME,
            postal_code     = TEST_POSTAL,
            rol             = UserRoleEnum.user,
            disabled        = False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[OK] Test user created: {TEST_EMAIL} (id={user.id})")
finally:
    db.close()

print(f"\nShared test credentials:")
print(f"  Email:    {TEST_EMAIL}")
print(f"  Password: {TEST_PASSWORD}")
