import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib


async def seed_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.uniform_db

    # User roles based on project charter
    users = [
        {
            "username": "ido26",  # Student persona
            "password": hashlib.sha256("student123".encode()).hexdigest(),
            "role": "student"
        },
        {
            "username": "anna_admin",  # Secretary persona
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "secretary"
        }
    ]

    await db.users.delete_many({})  # Clear existing to avoid duplicates
    await db.users.insert_many(users)
    print("Seed data inserted: Users 'ido26' and 'anna_admin' created.")


if __name__ == "__main__":
    asyncio.run(seed_data())
