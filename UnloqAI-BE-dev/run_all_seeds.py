import sys
import subprocess
import os
from app.db.session import SessionLocal
from app.services.oakfield.seed_meridian import seed_meridian_story


def run_command(command):
    print(f"🚀 Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(1)
    print("✅ Success.\n")

def main():
    print("=== 📦 UnloqAI Global Seeder ===\n")

    # 1. Run Alembic Migrations (Ensure DB Schema is current)
    print("1️⃣  Updating Database Schema (Alembic)...")
    run_command(f'"{sys.executable}" -m alembic upgrade head')

    # 2. Run Legacy Seed Script (Shared, Harper, Oakfield)
    # Using 'db' mode explicitly
    print("2️⃣  Seeding Shared/Harper/Oakfield Data...")
    run_command(f'"{sys.executable}" seed.py db')

    # 3. Run Meridian Seeder (Python Function)
    print("3️⃣  Seeding Meridian Strategy Story...")
    db = SessionLocal()
    try:
        seed_meridian_story(db)
        print("✅ Meridian Seeding Complete.")
    except Exception as e:
        print(f"❌ Meridian Seeding Failed: {e}")
    finally:
        db.close()

    print("\n🎉 All Seeding Operations Completed Successfully!")

if __name__ == "__main__":
    main()
