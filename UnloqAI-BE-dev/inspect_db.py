
from sqlalchemy import create_engine, inspect
from app.core.config import settings
import sys

# Patch pg8000 if needed (Alembic environment does it via imports, but here we might need it)
# Actually, sqlalchemy URL is what matters.

def list_tables():
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        check_tables = [
            'token_blacklist', 'users', 'meridian_kpis', 'oakfield_region_benchmarks',
            'harper_contracts', 'meridian_signals', 'harper_benchmarks',
            'oakfield_options_items', 'option_baskets', 'meridian_objectives',
            'meridian_recommendations', 'plots', 'meridian_issues',
            'oakfield_decision_bundles', 'options_catalog', 'bundles_catalog',
            'meridian_ledger'
        ]
        
        print("\n--- Table Existence Check ---")
        for table in check_tables:
            print(f"{table}: {table in tables}")
            
    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    list_tables()
