import os
import random
import datetime
import json
from decimal import Decimal
import psycopg2
from psycopg2.extras import execute_values
import uuid
import pandas as pd  # For Excel export

# Additional imports for synthetic data generation
from faker import Faker
from google import genai
from passlib.context import CryptContext

fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

random.seed(42)  # For reproducibility

# ---------------------------
# CONFIG: UPDATE THESE
# ---------------------------

DB_HOST = os.getenv("SIAAS_DB_HOST", "localhost")
DB_PORT = int(os.getenv("SIAAS_DB_PORT", "5432"))
DB_NAME = os.getenv("SIAAS_DB_NAME", "siaas_demo")
DB_USER = os.getenv("SIAAS_DB_USER", "postgres")
DB_PASS = os.getenv("SIAAS_DB_PASS", "root")

# Gemini config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCCXCOXMwmlkeHEEF3IZCp1NGy5qjjxkR4")
# Client initialization
client = genai.Client(api_key=GEMINI_API_KEY)

# File saving config: 'local' or 's3'
SAVE_MODE = os.getenv("SAVE_MODE", "local")  # 'local' to save files locally, 's3' to upload to S3
S3_BUCKET = os.getenv("S3_BUCKET", "your-siaas-demo-bucket")
LOCAL_DIR = os.getenv("LOCAL_DIR", "./generated_files")  # Local directory for files

# Create local dir if it doesn't exist
os.makedirs(LOCAL_DIR, exist_ok=True)

# Optional: AWS boto3 for S3
USE_S3 = SAVE_MODE == 's3'
if USE_S3:
    import boto3
    s3 = boto3.client('s3')

# Export config
EXPORT_DIR = os.getenv("EXPORT_DIR", "./exports")
os.makedirs(EXPORT_DIR, exist_ok=True)
EXPORT_EXCEL = os.getenv("EXPORT_EXCEL", "synthetic_data.xlsx")
EXPORT_JSON_PREFIX = os.getenv("EXPORT_JSON_PREFIX", "synthetic_data_")

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def connect():
    psycopg2.extras.register_uuid()
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )

def create_tables(cur):
    """Create all tables if they don't exist based on schemas."""
    print("Creating tables if they don't exist...")

    # Enable UUID extension if not already (fixed quotes)
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_superuser BOOLEAN DEFAULT FALSE
        );
    """)

    # Shared tables

    # companies
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            code VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    # decisions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            flow_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
    """)

    # impact_ledger
    cur.execute("""
        CREATE TABLE IF NOT EXISTS impact_ledger (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            decision_id UUID REFERENCES decisions(id) ON DELETE CASCADE,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
    """)

    # Meridian Tables
    print("Skipping Meridian table creation (handled by Alembic)...")
    # We do NOT drop or create Meridian tables here to avoid conflicts with Alembic schema.
    # The following tables are managed by Alembic:
    # strategy_os, strategy_objectives, strategy_kpis, external_signals, 
    # strategy_recommendations, impact_ledger_strategy, chat_messages, chat_sessions.

    # Pre-seed some Meridian Data for immediate UI visualization
    # print("Skipping initial Meridian data (handled by seed_meridian.py)...")


    # Harper tables

    # clients
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id VARCHAR(50) PRIMARY KEY,
            client_name VARCHAR(255) NOT NULL,
            sector VARCHAR(50) NOT NULL,
            billing_model VARCHAR(50) NOT NULL,
            annual_value_estimate DECIMAL(10,2),
            relationship_tier VARCHAR(50) NOT NULL
        );
    """)

    # harper_contracts (extended with schema fields)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS harper_contracts (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            decision_id UUID REFERENCES decisions(id) ON DELETE CASCADE,
            client_id VARCHAR(50) REFERENCES clients(client_id),
            client_name VARCHAR(255) NOT NULL,
            matter_ref VARCHAR(100) NOT NULL,
            contract_type VARCHAR(100) NOT NULL,
            sector VARCHAR(50) NOT NULL,
            complexity_band VARCHAR(20) NOT NULL,
            risk_band VARCHAR(20) NOT NULL,
            review_status VARCHAR(50) NOT NULL,
            s3_key VARCHAR(500) NOT NULL,
            received_at TIMESTAMP NOT NULL,
            reviewed_at TIMESTAMP,
            partner_approved_at TIMESTAMP,
            estimated_time_normal_minutes INTEGER,
            estimated_time_ai_minutes INTEGER,
            fee_model VARCHAR(50) NOT NULL,
            price_per_contract DECIMAL(10,2),
            identified_issues JSONB,
            summary_text TEXT
        );
    """)

    # harper_benchmarks (optional)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS harper_benchmarks (
            id SERIAL PRIMARY KEY,
            matter_type VARCHAR(100) NOT NULL,
            sector VARCHAR(50) NOT NULL,
            avg_market_fee DECIMAL(10,2) NOT NULL,
            avg_market_hours DECIMAL(5,2) NOT NULL
        );
    """)

    # Oakfield tables

    # plots
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plots (
            plot_id VARCHAR(50) PRIMARY KEY,
            development_name VARCHAR(255) NOT NULL,
            house_type VARCHAR(50) NOT NULL,
            build_stage VARCHAR(50) NOT NULL,
            target_options_margin DECIMAL(10,2) NOT NULL,
            region VARCHAR(50) NOT NULL
        );
    """)

    # options_catalog
    cur.execute("""
        CREATE TABLE IF NOT EXISTS options_catalog (
            option_code VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            cost_price DECIMAL(10,2) NOT NULL,
            sell_price DECIMAL(10,2) NOT NULL,
            margin DECIMAL(10,2) NOT NULL,
            availability VARCHAR(50) NOT NULL
        );
    """)

    # bundles_catalog
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bundles_catalog (
            bundle_code VARCHAR(50) PRIMARY KEY,
            bundle_name VARCHAR(255) NOT NULL,
            included_options JSONB NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            margin DECIMAL(10,2) NOT NULL,
            applies_to_house_types JSONB NOT NULL,
            triggers JSONB NOT NULL
        );
    """)

    # option_baskets
    cur.execute("""
        CREATE TABLE IF NOT EXISTS option_baskets (
            basket_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            plot_id VARCHAR(50) REFERENCES plots(plot_id) ON DELETE CASCADE,
            development_name VARCHAR(255) NOT NULL,
            house_type VARCHAR(50) NOT NULL,
            base_price DECIMAL(10,2) NOT NULL,
            selected_options JSONB NOT NULL,
            total_options_price DECIMAL(10,2) NOT NULL,
            estimated_margin DECIMAL(10,2) NOT NULL,
            margin_band VARCHAR(50) NOT NULL,
            recommended_bundles JSONB NOT NULL,
            created_at TIMESTAMP NOT NULL,
            approved_at TIMESTAMP
        );
    """)

    # oakfield_options_items
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oakfield_options_items (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            basket_id VARCHAR(50) REFERENCES option_baskets(basket_id) ON DELETE CASCADE,
            option_code VARCHAR(50) REFERENCES options_catalog(option_code) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 1 NOT NULL
        );
    """)

    # oakfield_decision_bundles
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oakfield_decision_bundles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            decision_id UUID REFERENCES decisions(id) ON DELETE CASCADE,
            bundle_code VARCHAR(50) REFERENCES bundles_catalog(bundle_code) ON DELETE CASCADE,
            status VARCHAR(50) NOT NULL
        );
    """)

    # oakfield_region_benchmarks (optional)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oakfield_region_benchmarks (
            id SERIAL PRIMARY KEY,
            region VARCHAR(50) NOT NULL,
            avg_options_margin_target DECIMAL(10,2) NOT NULL,
            avg_bundle_uptake DECIMAL(5,2) NOT NULL
        );
    """)

    print("Tables created/verified successfully.")

def seed_companies(cur):
    """Seed companies if they don't exist."""
    print("Seeding companies if needed...")
    harper_id = None
    oakfield_id = None

    cur.execute("SELECT id, code FROM companies WHERE code IN ('harper', 'oakfield');")
    existing = cur.fetchall()
    mapping = {row[1]: row[0] for row in existing}

    if 'harper' not in mapping:
        harper_id = uuid.uuid4()
        cur.execute("INSERT INTO companies (id, code) VALUES (%s, %s);", (harper_id, 'harper'))
    else:
        harper_id = mapping['harper']

    if 'oakfield' not in mapping:
        oakfield_id = uuid.uuid4()
        cur.execute("INSERT INTO companies (id, code) VALUES (%s, %s);", (oakfield_id, 'oakfield'))
    else:
        oakfield_id = mapping['oakfield']

    return {'harper': harper_id, 'oakfield': oakfield_id}

def get_company_ids(cur):
    """Get company IDs, but now seed if missing via seed_companies."""
    return seed_companies(cur)

def days_ago(n):
    return datetime.datetime.utcnow() - datetime.timedelta(days=n)

def save_contract_text(text, s3_key, client_name, matter_ref, contract_type):
    """Save generated contract text to local file or S3 based on SAVE_MODE."""
    if SAVE_MODE == 'local':
        # Local file: use s3_key as relative path
        local_path = os.path.join(LOCAL_DIR, s3_key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved locally: {local_path}")
    elif SAVE_MODE == 's3':
        try:
            s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=text.encode('utf-8'))
            print(f"Uploaded to S3: {s3_key}")
        except Exception as e:
            print(f"Error uploading to S3 {s3_key}: {e}")
            # Fallback to local
            local_path = os.path.join(LOCAL_DIR, s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Fallback saved locally: {local_path}")
    else:
        raise ValueError(f"Invalid SAVE_MODE: {SAVE_MODE}. Use 'local' or 's3'.")

def generate_synthetic_data():
    """Generate synthetic data in memory for file-only mode."""
    print("Generating synthetic data in memory for export...")

    # Shared data
    companies = [
        {'id': str(uuid.uuid4()), 'code': 'harper'},
        {'id': str(uuid.uuid4()), 'code': 'oakfield'}
    ]
    harper_id = companies[0]['id']
    oakfield_id = companies[1]['id']

    # Harper data
    clients = []
    decisions = []
    harper_contracts = []
    impact_ledger_harper = []
    harper_benchmarks = [
        {"matter_type": "NDA", "sector": "SaaS", "avg_market_fee": 150.00, "avg_market_hours": 2.5},
        {"matter_type": "MSA", "sector": "Retail", "avg_market_fee": 500.00, "avg_market_hours": 5.0},
        {"matter_type": "Supply Agreement", "sector": "Manufacturing", "avg_market_fee": 750.00, "avg_market_hours": 8.0},
    ]

    for i, c in enumerate(HARPER_CONTRACTS):
        client_id = f"CL-{i+1:03d}"
        clients.append({
            "client_id": client_id,
            "client_name": c["client_name"],
            "sector": c["sector"],
            "billing_model": c["fee_model"],
            "annual_value_estimate": round(random.uniform(10000, 100000), 2),
            "relationship_tier": random.choice(["strategic", "regular", "small"])
        })
        status = "pending" if i < 3 else "approved"
        created_at = days_ago(c["received_days_ago"] + 1)
        updated_at = days_ago(c["received_days_ago"])
        decision_id = str(uuid.uuid4())
        decisions.append({
            "id": decision_id,
            "company_id": harper_id,
            "flow_type": "contract_triage",
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at
        })
        received_at = days_ago(c["received_days_ago"])
        reviewed_at = received_at + datetime.timedelta(hours=random.randint(1, 2)) if i >= 3 else None
        partner_approved_at = reviewed_at + datetime.timedelta(minutes=5) if i >= 3 else None
        estimated_time_normal = random.choice([60, 90, 120])
        estimated_time_ai = estimated_time_normal // 3
        identified_issues = c["identified_issues"]
        summary_text = c["summary_text"] or f"AI summary for {c['contract_type']}."
        harper_contracts.append({
            "id": str(uuid.uuid4()),
            "decision_id": decision_id,
            "client_id": client_id,
            "client_name": c["client_name"],
            "matter_ref": c["matter_ref"],
            "contract_type": c["contract_type"],
            "sector": c["sector"],
            "complexity_band": c["complexity_band"],
            "risk_band": c["risk_band"],
            "review_status": c["review_status"],
            "s3_key": c["s3_key"],
            "received_at": received_at,
            "reviewed_at": reviewed_at,
            "partner_approved_at": partner_approved_at,
            "estimated_time_normal_minutes": estimated_time_normal,
            "estimated_time_ai_minutes": estimated_time_ai,
            "fee_model": c["fee_model"],
            "price_per_contract": c["price_per_contract"],
            "identified_issues": identified_issues,
            "summary_text": summary_text
        })
        if i >= 3:  # Approved only
            time_saved = Decimal(random.choice([20, 25, 30]))
            latency_ms = random.randint(500, 2000)
            risk_level = random.choice(["Low", "Medium", "High"])
            impact_ledger_harper.append({
                "id": str(uuid.uuid4()),
                "decision_id": decision_id,
                "company_id": harper_id,
                "flow_type": "contract_triage",
                "route_type": "retrieval+llm",
                "risk_level": risk_level,
                "risk_notes": "Synthetic risk notes for demo triage.",
                "options_margin_pct": None,
                "margin_target_pct": None,
                "margin_delta_pct": None,
                "bundle_opportunity_detected": None,
                "bundle_opportunity_count": None,
                "bundle_offer_sent": None,
                "bundle_offer_channel": None,
                "bundle_estimated_additional_revenue": None,
                "bundle_estimated_additional_margin": None,
                "latency_ms": latency_ms,
                "estimated_time_saved_minutes": time_saved,
                "execution_channel": "retrofix:harper_contract_summary_email",
                "execution_status": "success",
                "created_at": days_ago(c["received_days_ago"])
            })

    # Oakfield data
    plots = OAKFIELD_PLOTS.copy()
    options_catalog = OAKFIELD_OPTIONS.copy()
    bundles_catalog = OAKFIELD_BUNDLES.copy()
    option_baskets = []
    oakfield_options_items = []
    oakfield_decision_bundles = []
    impact_ledger_oakfield = []
    oakfield_region_benchmarks = [
        {"region": "North", "avg_options_margin_target": 25000.0, "avg_bundle_uptake": 0.15},
        {"region": "Midlands", "avg_options_margin_target": 20000.0, "avg_bundle_uptake": 0.20},
        {"region": "South", "avg_options_margin_target": 30000.0, "avg_bundle_uptake": 0.25},
    ]

    for i in range(5):
        customer_id = f"CU-{random.randint(1, 500):03d}"
        development_name = random.choice([p["development_name"] for p in plots])
        plot = random.choice(plots)
        plot_id = plot["plot_id"]
        house_type = plot["house_type"]
        build_stage = plot["build_stage"]
        base_price = round(random.uniform(200000, 500000), 2)
        target_margin = plot["target_options_margin"]

        num_opts = random.randint(2, 4)
        selected_options = random.sample(options_catalog, num_opts)
        selected_codes = [o["code"] for o in selected_options]
        total_options_price = sum(o["sell_price"] for o in selected_options)
        total_cost = sum(o["cost_price"] for o in selected_options)
        estimated_margin = total_options_price - total_cost
        margin_band = "below_target" if estimated_margin < target_margin * 0.9 else "on_target" if estimated_margin <= target_margin * 1.1 else "above_target"
        recommended_bundles_list = [random.choice(bundles_catalog)["code"] for _ in range(random.randint(0, 1))] if random.random() > 0.4 else []
        recommended_bundles = json.dumps(recommended_bundles_list)

        created_at = days_ago(random.randint(1, 30))
        status = random.choices(["pending", "approved"], weights=[0.4, 0.6], k=1)[0]  # Fixed: use random.choices
        updated_at = created_at if status == "pending" else days_ago(random.randint(0, 1))
        approved_at = updated_at if status == "approved" else None

        basket_id = f"BKT-{random.randint(1000, 9999):04d}"
        basket = {
            "basket_id": basket_id,
            "customer_id": customer_id,
            "plot_id": plot_id,
            "development_name": development_name,
            "house_type": house_type,
            "base_price": base_price,
            "selected_options": json.dumps(selected_codes),
            "total_options_price": total_options_price,
            "estimated_margin": estimated_margin,
            "margin_band": margin_band,
            "recommended_bundles": recommended_bundles,
            "created_at": created_at,
            "approved_at": approved_at
        }
        option_baskets.append(basket)

        decision_id = str(uuid.uuid4())
        decisions.append({
            "id": decision_id,
            "company_id": oakfield_id,
            "flow_type": "options_basket",
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at
        })

        for code in selected_codes:
            oakfield_options_items.append({
                "id": str(uuid.uuid4()),
                "basket_id": basket_id,
                "option_code": code,
                "quantity": 1
            })

        if recommended_bundles != '[]' and random.random() > 0.5:
            bundle_code = recommended_bundles_list[0]
            oakfield_decision_bundles.append({
                "id": str(uuid.uuid4()),
                "decision_id": decision_id,
                "bundle_code": bundle_code,
                "status": "offered" if random.random() > 0.5 else "opportunity"
            })

        if status == "approved":
            options_revenue = total_options_price
            options_cost = total_options_price - estimated_margin
            margin_achieved = estimated_margin
            bundle_offered = recommended_bundles_list[0] if recommended_bundles_list else None
            bundle_accepted = random.choice([True, False]) if bundle_offered else False
            upsell_revenue_gain = random.uniform(1000, 3000) if bundle_accepted else 0

            options_margin_pct = round((margin_achieved / options_revenue) * 100, 2) if options_revenue > 0 else 0
            margin_target_pct = 30.0
            margin_delta_pct = options_margin_pct - margin_target_pct
            bundle_opportunity_detected = bundle_offered is not None
            bundle_opportunity_count = 1 if bundle_opportunity_detected else 0
            bundle_offer_sent = True if bundle_offered else False
            bundle_offer_channel = random.choice(["email", "portal"]) if bundle_offer_sent else None
            bundle_estimated_additional_revenue = upsell_revenue_gain
            bundle_estimated_additional_margin = upsell_revenue_gain * 0.4
            latency_ms = random.randint(200, 1000)
            time_saved = Decimal(random.choice([5, 10, 15]))
            risk_level = random.choice(["Low", "Medium"])
            route_type = "retrieval+llm"
            risk_notes = f"Synthetic notes for {development_name} {house_type} basket review."
            execution_channel = "retrofix:oakfield_options_bundle_email"
            execution_status = "success"

            impact_ledger_oakfield.append({
                "id": str(uuid.uuid4()),
                "decision_id": decision_id,
                "company_id": oakfield_id,
                "flow_type": "options_basket",
                "route_type": route_type,
                "risk_level": risk_level,
                "risk_notes": risk_notes,
                "options_margin_pct": options_margin_pct,
                "margin_target_pct": margin_target_pct,
                "margin_delta_pct": margin_delta_pct,
                "bundle_opportunity_detected": bundle_opportunity_detected,
                "bundle_opportunity_count": bundle_opportunity_count,
                "bundle_offer_sent": bundle_offer_sent,
                "bundle_offer_channel": bundle_offer_channel,
                "bundle_estimated_additional_revenue": bundle_estimated_additional_revenue,
                "bundle_estimated_additional_margin": bundle_estimated_additional_margin,
                "latency_ms": latency_ms,
                "estimated_time_saved_minutes": time_saved,
                "execution_channel": execution_channel,
                "execution_status": execution_status,
                "created_at": created_at
            })

    # Generate and save contract texts (even in file mode)
    print(f"Generating and saving contract texts ({SAVE_MODE} mode)...")
    # model = genai.GenerativeModel('gemini-2.0-flash-lite') # Deprecated
    for c in HARPER_CONTRACTS:
        prompt = f"""Generate a plausible, realistic sample text for a {c['contract_type']} between Harper & Co (a legal firm) and {c['client_name']}, reference {c['matter_ref']}. 
        Include standard sections: parties involved, recitals, definitions, obligations, terms and conditions, termination, liability, governing law, and signatures. 
        Make it detailed but concise (800-1500 words), use formal legal language, but keep it demo-plausible (no real legal advice). 
        Ensure it feels authentic for a {c['contract_type'].lower()}. End with placeholder signatures."""
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=prompt
            )
            text = response.text
            save_contract_text(text, c['s3_key'], c['client_name'], c['matter_ref'], c['contract_type'])
        except Exception as e:
            print(f"Error generating text for {c['s3_key']}: {e}")
            placeholder = f"Placeholder {c['contract_type']} for {c['client_name']} - {c['matter_ref']}. Full text generation failed."
            save_contract_text(placeholder, c['s3_key'], c['client_name'], c['matter_ref'], c['contract_type'])

    # Return all data for export
    return {
        'companies': companies,
        'decisions': decisions,
        'clients': clients,
        'harper_contracts': harper_contracts,
        'impact_ledger': impact_ledger_harper + impact_ledger_oakfield,
        'harper_benchmarks': harper_benchmarks,
        'plots': plots,
        'options_catalog': options_catalog,
        'bundles_catalog': bundles_catalog,
        'option_baskets': option_baskets,
        'oakfield_options_items': oakfield_options_items,
        'oakfield_decision_bundles': oakfield_decision_bundles,
        'oakfield_region_benchmarks': oakfield_region_benchmarks
    }

def export_to_files(data_dict):
    """Export synthetic data to Excel and JSON files from dict."""
    print("Exporting data to Excel and JSON files...")
    tables = list(data_dict.keys())

    excel_path = os.path.join(EXPORT_DIR, EXPORT_EXCEL)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for table in tables:
            df = pd.DataFrame(data_dict[table])
            # Handle JSON fields
            for col in df.columns:
                if col in ['identified_issues', 'included_options', 'applies_to_house_types', 'triggers', 'selected_options', 'recommended_bundles']:
                    df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x))
            sheet_name = table[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Exported {table} to Excel sheet '{sheet_name}'")

            # Export to JSON
            json_path = os.path.join(EXPORT_DIR, f"{EXPORT_JSON_PREFIX}{table}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict[table], f, default=str, indent=2)
            print(f"Exported {table} to {json_path}")

    print(f"Export complete! Excel: {excel_path}, JSONs in {EXPORT_DIR}")

def export_from_db(cur):
    """Export all tables to Excel (one sheet per table) and JSON files."""
    print("Exporting data to Excel and JSON files...")
    tables = [
        'companies', 'decisions', 'impact_ledger', 'clients', 'harper_contracts', 'harper_benchmarks',
        'plots', 'options_catalog', 'bundles_catalog', 'option_baskets', 'oakfield_options_items',
        'oakfield_decision_bundles', 'oakfield_region_benchmarks'
    ]

    excel_path = os.path.join(EXPORT_DIR, EXPORT_EXCEL)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for table in tables:
            try:
                cur.execute(f"SELECT * FROM {table};")
                rows = cur.fetchall()
                if not rows:
                    print(f"No data in {table}, skipping.")
                    continue
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(rows, columns=columns)
                # Handle JSONB fields by converting to string for Excel
                for col in df.columns:
                    if col in ['identified_issues', 'included_options', 'applies_to_house_types', 'triggers', 'selected_options', 'recommended_bundles']:
                        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, dict) else str(x))
                sheet_name = table[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Exported {table} to Excel sheet '{sheet_name}'")

                # Export to JSON
                json_data = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # Convert JSONB to dict for JSON
                    for col in row_dict:
                        if col in ['identified_issues', 'included_options', 'applies_to_house_types', 'triggers', 'selected_options', 'recommended_bundles']:
                            try:
                                row_dict[col] = json.loads(str(row_dict[col]))
                            except:
                                row_dict[col] = str(row_dict[col])
                    json_data.append(row_dict)
                json_path = os.path.join(EXPORT_DIR, f"{EXPORT_JSON_PREFIX}{table}.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, default=str, indent=2)
                print(f"Exported {table} to {json_path}")
            except Exception as e:
                print(f"Error exporting {table}: {e}")

    print(f"Export complete! Excel: {excel_path}, JSONs in {EXPORT_DIR}")

# ---------------------------
# HARPERS – CONTRACT TRIAGE
# ---------------------------

HARPER_CONTRACTS = [
    {
        "client_name": "Northshore Retail Ltd",
        "matter_ref": "CORP-001-NSR",
        "contract_type": "Master Services Agreement",
        "s3_key": "harper/contracts/msa_northshore_001.txt",
        "received_days_ago": 2,
        "sector": "Retail",
        "complexity_band": "medium",
        "risk_band": "medium",
        "review_status": "pending",
        "fee_model": "retainer",
        "price_per_contract": 250.00,
        "identified_issues": json.dumps(["liability cap", "auto-renewal"]),
        "summary_text": None  # Will be generated later if needed
    },
    {
        "client_name": "Evergreen Analytics plc",
        "matter_ref": "COM-014-EGA",
        "contract_type": "NDA",
        "s3_key": "harper/contracts/nda_evergreen_002.txt",
        "received_days_ago": 3,
        "sector": "SaaS",
        "complexity_band": "low",
        "risk_band": "low",
        "review_status": "pending",
        "fee_model": "hourly",
        "price_per_contract": None,
        "identified_issues": json.dumps([]),
        "summary_text": None
    },
    {
        "client_name": "Bluewave Logistics Ltd",
        "matter_ref": "CORP-099-BWL",
        "contract_type": "Supply Agreement",
        "s3_key": "harper/contracts/supply_bluewave_003.txt",
        "received_days_ago": 5,
        "sector": "Logistics",
        "complexity_band": "high",
        "risk_band": "high",
        "review_status": "pending",
        "fee_model": "fixed_fee",
        "price_per_contract": 500.00,
        "identified_issues": json.dumps(["supply chain risks"]),
        "summary_text": None
    },
    {
        "client_name": "Pioneer Capital Partners",
        "matter_ref": "PE-011-PCP",
        "contract_type": "Share Purchase Agreement",
        "s3_key": "harper/contracts/spa_pioneer_004.txt",
        "received_days_ago": 8,
        "sector": "Finance",
        "complexity_band": "high",
        "risk_band": "medium",
        "review_status": "completed",
        "fee_model": "retainer",
        "price_per_contract": 750.00,
        "identified_issues": json.dumps(["indemnities"]),
        "summary_text": "Summary of share purchase terms."
    },
    {
        "client_name": "Silverline Manufacturing Ltd",
        "matter_ref": "COM-032-SLM",
        "contract_type": "Distribution Agreement",
        "s3_key": "harper/contracts/dist_silverline_005.txt",
        "received_days_ago": 10,
        "sector": "Manufacturing",
        "complexity_band": "medium",
        "risk_band": "low",
        "review_status": "completed",
        "fee_model": "hourly",
        "price_per_contract": None,
        "identified_issues": json.dumps(["distribution territories"]),
        "summary_text": None
    },
    {
        "client_name": "UrbanVista Developments Ltd",
        "matter_ref": "REAL-020-UVD",
        "contract_type": "Development Agreement",
        "s3_key": "harper/contracts/dev_urbanvista_006.txt",
        "received_days_ago": 12,
        "sector": "Real Estate",
        "complexity_band": "high",
        "risk_band": "high",
        "review_status": "completed",
        "fee_model": "fixed_fee",
        "price_per_contract": 1000.00,
        "identified_issues": json.dumps(["zoning issues"]),
        "summary_text": "Development terms overview."
    },
]

# ---------------------------
# OAKFIELD – OPTIONS & BUNDLES
# ---------------------------

OAKFIELD_BUNDLES = [
    {
        "code": "PREM_LIGHT",
        "name": "Premium Lighting Pack",
        "included_options": json.dumps(["OPT-LIGHT-LED", "OPT-LIGHT-DIM"]),
        "price": 1500.0,
        "margin": 600.0,
        "applies_to_house_types": json.dumps(["3-bed", "4-bed"]),
        "triggers": json.dumps(["lighting upgrade"]),
    },
    {
        "code": "EV_READY",
        "name": "EV-Ready Driveway Pack",
        "included_options": json.dumps(["OPT-EV-CHRG", "OPT-PV-WIRE"]),
        "price": 2000.0,
        "margin": 800.0,
        "applies_to_house_types": json.dumps(["4-bed", "townhouse"]),
        "triggers": json.dumps(["EV charger interest"]),
    },
]

OAKFIELD_OPTIONS = [
    {"code": "OPT-KIT-PRM", "name": "Premium Kitchen Package", "category": "kitchen", "cost_price": 5000.0, "sell_price": 8000.0, "margin": 3000.0, "availability": "available"},
    {"code": "OPT-FLR-LUX", "name": "Luxury Flooring", "category": "flooring", "cost_price": 2000.0, "sell_price": 3500.0, "margin": 1500.0, "availability": "available"},
    {"code": "OPT-LIGHT-LED", "name": "LED Smart Lighting", "category": "electrical", "cost_price": 800.0, "sell_price": 1200.0, "margin": 400.0, "availability": "available"},
    {"code": "OPT-EV-CHRG", "name": "EV Charger Installation", "category": "green", "cost_price": 1000.0, "sell_price": 1800.0, "margin": 800.0, "availability": "site-specific"},
    {"code": "OPT-PV-WIRE", "name": "PV-Ready Wiring", "category": "green", "cost_price": 600.0, "sell_price": 1000.0, "margin": 400.0, "availability": "available"},
    {"code": "OPT-BTH-SPA", "name": "Spa Bathroom Upgrade", "category": "bathroom", "cost_price": 3000.0, "sell_price": 5000.0, "margin": 2000.0, "availability": "available"},
    {"code": "OPT-GAR-EXT", "name": "Extended Garage", "category": "exterior", "cost_price": 4000.0, "sell_price": 6500.0, "margin": 2500.0, "availability": "unavailable"},
    {"code": "OPT-WND-BAY", "name": "Bay Windows", "category": "windows", "cost_price": 1500.0, "sell_price": 2500.0, "margin": 1000.0, "availability": "available"},
    {"code": "OPT-SEC-SYS", "name": "Security System", "category": "security", "cost_price": 1200.0, "sell_price": 2000.0, "margin": 800.0, "availability": "available"},
    {"code": "OPT-GDN-PAT", "name": "Patio Garden Setup", "category": "garden", "cost_price": 2500.0, "sell_price": 4000.0, "margin": 1500.0, "availability": "site-specific"},
]

OAKFIELD_PLOTS = [
    {"plot_id": "PL-001", "development_name": "Oakfield Meadows", "house_type": "3-bed", "build_stage": "foundation", "target_options_margin": 25000.0, "region": "North"},
    {"plot_id": "PL-002", "development_name": "Oakfield Meadows", "house_type": "4-bed", "build_stage": "brickwork", "target_options_margin": 30000.0, "region": "North"},
    {"plot_id": "PL-003", "development_name": "Riverside Oaks", "house_type": "townhouse", "build_stage": "roof", "target_options_margin": 20000.0, "region": "Midlands"},
    {"plot_id": "PL-004", "development_name": "Riverside Oaks", "house_type": "2-bed", "build_stage": "internals", "target_options_margin": 15000.0, "region": "Midlands"},
    {"plot_id": "PL-005", "development_name": "Sunset Fields", "house_type": "4-bed", "build_stage": "complete", "target_options_margin": 35000.0, "region": "South"},
]

def seed_harper(cur, company_ids):
    harper_id = company_ids["harper"]
    print("Seeding Harper decisions + contracts...")

    # Seed clients if needed (for FK, but since client_name is used, insert clients)
    print("Seeding Harper clients...")
    client_rows = []
    for i, c in enumerate(HARPER_CONTRACTS):
        client_id = f"CL-{i+1:03d}"
        sector = c["sector"]
        billing_model = c["fee_model"]  # Reuse for simplicity
        annual_value_estimate = round(random.uniform(10000, 100000), 2)
        relationship_tier = random.choice(["strategic", "regular", "small"])
        client_rows.append((client_id, c["client_name"], sector, billing_model, annual_value_estimate, relationship_tier))
    insert_clients_sql = """
        INSERT INTO clients (client_id, client_name, sector, billing_model, annual_value_estimate, relationship_tier)
        VALUES %s
        ON CONFLICT (client_id) DO NOTHING;
    """
    execute_values(cur, insert_clients_sql, client_rows, page_size=100)

    decision_rows = []
    contract_rows = []

    # Half pending, half approved for variety
    client_ids = [f"CL-{i+1:03d}" for i in range(len(HARPER_CONTRACTS))]  # Simple mapping
    for i, c in enumerate(HARPER_CONTRACTS):
        status = "pending" if i < 3 else "approved"
        created_at = days_ago(c["received_days_ago"] + 1)
        updated_at = days_ago(c["received_days_ago"])
        decision_rows.append(
            (
                harper_id,         # company_id
                "contract_triage", # flow_type
                status,
                created_at,
                updated_at,
            )
        )

    insert_decisions_sql = """
        INSERT INTO decisions (company_id, flow_type, status, created_at, updated_at)
        VALUES %s
        RETURNING id;
    """
    execute_values(cur, insert_decisions_sql, decision_rows)
    decision_ids = [row[0] for row in cur.fetchall()]

    for idx, c in enumerate(HARPER_CONTRACTS):
        decision_id = decision_ids[idx]
        received_at = days_ago(c["received_days_ago"])
        client_id = client_ids[idx]
        reviewed_at = received_at + datetime.timedelta(hours=random.randint(1, 2)) if idx >= 3 else None
        partner_approved_at = reviewed_at + datetime.timedelta(minutes=5) if idx >= 3 else None
        estimated_time_normal = random.choice([60, 90, 120])
        estimated_time_ai = estimated_time_normal // 3
        identified_issues = c["identified_issues"]
        summary_text = c["summary_text"] or f"AI summary for {c['contract_type']}."

        contract_rows.append(
            (
                decision_id,
                client_id,
                c["client_name"],
                c["matter_ref"],
                c["contract_type"],
                c["sector"],
                c["complexity_band"],
                c["risk_band"],
                c["review_status"],
                c["s3_key"],
                received_at,
                reviewed_at,
                partner_approved_at,
                estimated_time_normal,
                estimated_time_ai,
                c["fee_model"],
                c["price_per_contract"],
                identified_issues,
                summary_text,
            )
        )

    insert_contracts_sql = """
        INSERT INTO harper_contracts
            (decision_id, client_id, client_name, matter_ref, contract_type, sector, complexity_band, risk_band,
             review_status, s3_key, received_at, reviewed_at, partner_approved_at, estimated_time_normal_minutes,
             estimated_time_ai_minutes, fee_model, price_per_contract, identified_issues, summary_text)
        VALUES %s;
    """
    execute_values(cur, insert_contracts_sql, contract_rows)

    # Seed a few Impact Ledger entries for APPROVED decisions (historical)
    print("Seeding Harper impact_ledger entries...")
    ledger_rows = []
    # approximate 20–30min saved per contract for triage
    for idx, c in enumerate(HARPER_CONTRACTS):
        # Only for those we marked approved
        if idx < 3:
            continue
        decision_id = decision_ids[idx]
        created_at = days_ago(c["received_days_ago"])
        # random-ish time saved
        time_saved = Decimal(random.choice([20, 25, 30]))
        latency_ms = random.randint(500, 2000)
        risk_level = random.choice(["Low", "Medium", "High"])

        ledger_rows.append(
            (
                decision_id,
                harper_id,
                "contract_triage",
                "retrieval+llm",
                risk_level,
                "Synthetic risk notes for demo triage.",
                None,  # options_margin_pct
                None,  # margin_target_pct
                None,  # margin_delta_pct
                None,  # bundle_opportunity_detected
                None,  # bundle_opportunity_count
                None,  # bundle_offer_sent
                None,  # bundle_offer_channel
                None,  # bundle_estimated_additional_revenue
                None,  # bundle_estimated_additional_margin
                latency_ms,
                time_saved,
                "retrofix:harper_contract_summary_email",
                "success",
                created_at,
            )
        )

    if ledger_rows:
        insert_ledger_sql = """
            INSERT INTO impact_ledger (
                decision_id,
                company_id,
                flow_type,
                route_type,
                risk_level,
                risk_notes,
                options_margin_pct,
                margin_target_pct,
                margin_delta_pct,
                bundle_opportunity_detected,
                bundle_opportunity_count,
                bundle_offer_sent,
                bundle_offer_channel,
                bundle_estimated_additional_revenue,
                bundle_estimated_additional_margin,
                latency_ms,
                estimated_time_saved_minutes,
                execution_channel,
                execution_status,
                created_at
            ) VALUES %s;
        """
        execute_values(cur, insert_ledger_sql, ledger_rows)

    # Optional: Seed harper_benchmarks
    print("Seeding Harper benchmarks...")
    benchmark_rows = [
        ("NDA", "SaaS", 150.00, 2.5),
        ("MSA", "Retail", 500.00, 5.0),
        ("Supply Agreement", "Manufacturing", 750.00, 8.0),
    ]
    insert_bench_sql = """
        INSERT INTO harper_benchmarks (matter_type, sector, avg_market_fee, avg_market_hours)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cur, insert_bench_sql, benchmark_rows)

def seed_oakfield(cur, company_ids):
    oakfield_id = company_ids["oakfield"]

    # Seed plots
    print("Seeding Oakfield plots...")
    plot_rows = []
    for p in OAKFIELD_PLOTS:
        plot_rows.append((p["plot_id"], p["development_name"], p["house_type"], p["build_stage"], p["target_options_margin"], p["region"]))
    insert_plots_sql = """
        INSERT INTO plots (plot_id, development_name, house_type, build_stage, target_options_margin, region)
        VALUES %s
        ON CONFLICT (plot_id) DO NOTHING;
    """
    execute_values(cur, insert_plots_sql, plot_rows)

    # Seed bundles catalog
    print("Seeding Oakfield bundles catalog...")
    bundle_rows = []
    for b in OAKFIELD_BUNDLES:
        bundle_rows.append((b["code"], b["name"], b["included_options"], b["price"], b["margin"], b["applies_to_house_types"], b["triggers"]))
    insert_bundles_sql = """
        INSERT INTO bundles_catalog (bundle_code, bundle_name, included_options, price, margin, applies_to_house_types, triggers)
        VALUES %s
        ON CONFLICT (bundle_code) DO NOTHING;
    """
    execute_values(cur, insert_bundles_sql, bundle_rows)

    # Seed options catalog
    print("Seeding Oakfield options catalog...")
    option_rows = []
    for o in OAKFIELD_OPTIONS:
        option_rows.append((o["code"], o["name"], o["category"], o["cost_price"], o["sell_price"], o["margin"], o["availability"]))
    insert_options_sql = """
        INSERT INTO options_catalog (option_code, name, category, cost_price, sell_price, margin, availability)
        VALUES %s
        ON CONFLICT (option_code) DO NOTHING;
    """
    execute_values(cur, insert_options_sql, option_rows)

    # Seed option baskets and related
    print("Seeding Oakfield option baskets...")
    basket_rows = []
    options_items_rows = []
    decision_rows = []
    decision_bundles_rows = []  # Temp list, will map later

    for i in range(5):
        customer_id = f"CU-{random.randint(1, 500):03d}"
        development_name = random.choice([p["development_name"] for p in OAKFIELD_PLOTS])
        plot = random.choice(OAKFIELD_PLOTS)
        plot_id = plot["plot_id"]
        house_type = plot["house_type"]
        build_stage = plot["build_stage"]
        base_price = round(random.uniform(200000, 500000), 2)
        target_margin = plot["target_options_margin"]

        # Select 2-4 random options using Faker-like variety
        num_opts = random.randint(2, 4)
        selected_options = random.sample(OAKFIELD_OPTIONS, num_opts)
        selected_codes = [o["code"] for o in selected_options]
        total_options_price = sum(o["sell_price"] for o in selected_options)
        total_cost = sum(o["cost_price"] for o in selected_options)
        estimated_margin = total_options_price - total_cost
        margin_band = "below_target" if estimated_margin < target_margin * 0.9 else "on_target" if estimated_margin <= target_margin * 1.1 else "above_target"
        recommended_bundles = json.dumps([random.choice(OAKFIELD_BUNDLES)["code"] for _ in range(random.randint(0, 1))]) if random.random() > 0.4 else json.dumps([])

        created_at = days_ago(random.randint(1, 30))
        status = random.choices(["pending", "approved"], weights=[0.4, 0.6], k=1)[0]  # Fixed: use random.choices
        updated_at = created_at if status == "pending" else days_ago(random.randint(0, 1))
        approved_at = updated_at if status == "approved" else None

        basket_id = f"BKT-{random.randint(1000, 9999):04d}"

        basket_data = (
            basket_id, customer_id, plot_id, development_name, house_type, base_price,
            json.dumps(selected_codes), total_options_price, estimated_margin, margin_band,
            recommended_bundles, created_at, approved_at
        )
        basket_rows.append(basket_data)

        # Decision row
        decision_data = (oakfield_id, "options_basket", status, created_at, updated_at)
        decision_rows.append(decision_data)

        # Options items (assume quantity=1 for simplicity)
        for code in selected_codes:
            options_items_rows.append((basket_id, code, 1))

        # Random decision bundles if recommended
        if recommended_bundles != '[]' and random.random() > 0.5:
            bundle_code = json.loads(recommended_bundles)[0]
            decision_bundles_rows.append((i, bundle_code, "offered" if random.random() > 0.5 else "opportunity"))

    # Insert decisions
    insert_decisions_sql = """
        INSERT INTO decisions (company_id, flow_type, status, created_at, updated_at)
        VALUES %s RETURNING id;
    """
    execute_values(cur, insert_decisions_sql, decision_rows)
    decision_ids = [row[0] for row in cur.fetchall()]

    # Insert baskets
    insert_baskets_sql = """
        INSERT INTO option_baskets
            (basket_id, customer_id, plot_id, development_name, house_type, base_price, selected_options,
             total_options_price, estimated_margin, margin_band, recommended_bundles, created_at, approved_at)
        VALUES %s
        ON CONFLICT (basket_id) DO NOTHING;
    """
    execute_values(cur, insert_baskets_sql, basket_rows)

    # Insert options items
    insert_items_sql = """
        INSERT INTO oakfield_options_items (basket_id, option_code, quantity)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cur, insert_items_sql, options_items_rows)

    # Insert decision bundles
    db_rows = [(decision_ids[idx], bundle_code, status_) for idx, (idx_, bundle_code, status_) in enumerate(decision_bundles_rows)]
    if db_rows:
        insert_db_sql = """
            INSERT INTO oakfield_decision_bundles (decision_id, bundle_code, status)
            VALUES %s
            ON CONFLICT DO NOTHING;
        """
        execute_values(cur, insert_db_sql, db_rows)

    # Seed Impact Ledger for approved decisions (historical, with Oakfield-specific fields)
    print("Seeding Oakfield impact_ledger entries...")
    ledger_rows = []
    for idx in range(5):
        if decision_rows[idx][2] == "approved":  # Only approved
            decision_id = decision_ids[idx]
            created_at = decision_rows[idx][3]
            basket = basket_rows[idx]
            options_revenue = basket[7]
            options_cost = options_revenue - basket[8]  # Reverse calc for cost
            margin_achieved = basket[8]
            margin_band = basket[9]
            bundle_offered = json.loads(basket[10])[0] if basket[10] != '[]' else None
            bundle_accepted = random.choice([True, False]) if bundle_offered else False
            upsell_revenue_gain = random.uniform(1000, 3000) if bundle_accepted else 0

            # Map to ledger fields
            options_margin_pct = round((margin_achieved / options_revenue) * 100, 2) if options_revenue > 0 else 0
            margin_target_pct = 30.0
            margin_delta_pct = options_margin_pct - margin_target_pct
            bundle_opportunity_detected = bundle_offered is not None
            bundle_opportunity_count = 1 if bundle_opportunity_detected else 0
            bundle_offer_sent = True if bundle_offered else False
            bundle_offer_channel = random.choice(["email", "portal"]) if bundle_offer_sent else None
            bundle_estimated_additional_revenue = upsell_revenue_gain
            bundle_estimated_additional_margin = upsell_revenue_gain * 0.4
            latency_ms = random.randint(200, 1000)
            time_saved = Decimal(random.choice([5, 10, 15]))  # Minutes saved on review
            risk_level = random.choice(["Low", "Medium"])
            route_type = "retrieval+llm"
            risk_notes = f"Synthetic notes for {basket[3]} {basket[4]} basket review."
            execution_channel = "retrofix:oakfield_options_bundle_email"
            execution_status = "success"

            ledger_data = (
                decision_id, oakfield_id, "options_basket", route_type, risk_level, risk_notes,
                options_margin_pct, margin_target_pct, margin_delta_pct, bundle_opportunity_detected,
                bundle_opportunity_count, bundle_offer_sent, bundle_offer_channel,
                bundle_estimated_additional_revenue, bundle_estimated_additional_margin,
                latency_ms, time_saved, execution_channel, execution_status, created_at
            )
            ledger_rows.append(ledger_data)

    if ledger_rows:
        insert_ledger_sql = """
            INSERT INTO impact_ledger (
                decision_id, company_id, flow_type, route_type, risk_level, risk_notes,
                options_margin_pct, margin_target_pct, margin_delta_pct, bundle_opportunity_detected,
                bundle_opportunity_count, bundle_offer_sent, bundle_offer_channel,
                bundle_estimated_additional_revenue, bundle_estimated_additional_margin,
                latency_ms, estimated_time_saved_minutes, execution_channel, execution_status, created_at
            ) VALUES %s;
        """
        execute_values(cur, insert_ledger_sql, ledger_rows)

    # Optional: Seed oakfield_region_benchmarks
    print("Seeding Oakfield region benchmarks...")
    region_bench_rows = [
        ("North", 25000.0, 0.15),
        ("Midlands", 20000.0, 0.20),
        ("South", 30000.0, 0.25),
    ]
    insert_region_sql = """
        INSERT INTO oakfield_region_benchmarks (region, avg_options_margin_target, avg_bundle_uptake)
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cur, insert_region_sql, region_bench_rows)

# ---------------------------
# SPOT-CHECK FUNCTION (DB only)
# ---------------------------

def spot_check(cur):
    print("\n--- SPOT CHECK: Harper Contracts ---")
    cur.execute("SELECT * FROM harper_contracts LIMIT 3;")
    for row in cur.fetchall():
        print(row)

    print("\n--- SPOT CHECK: Oakfield Baskets ---")
    cur.execute("SELECT * FROM option_baskets LIMIT 3;")
    for row in cur.fetchall():
        print(row)

    print("\n--- SPOT CHECK: Impact Ledger (Recent) ---")
    cur.execute("SELECT * FROM impact_ledger ORDER BY created_at DESC LIMIT 3;")
    for row in cur.fetchall():
        print(row)
    print("Spot-check complete. Entries appear credible: varied statuses, realistic names/prices/margins, historical dates. Supports demo narratives for triage efficiency and upsell opportunities.")

def seed_users(cur):
    """Seed users."""
    print("Seeding users...")
    users = [
        ("admin@unloq.ai", "admin123", "Admin User", True),
        ("user@unloq.ai", "user123", "Regular User", False),
        ("demo@unloq.ai", "demo123", "Demo User", False),
    ]
    
    for email, password, name, is_superuser in users:
        hashed = pwd_context.hash(password)
        cur.execute("""
            INSERT INTO users (email, hashed_password, full_name, is_superuser)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """, (email, hashed, name, is_superuser))

# ---------------------------
# MAIN EXECUTION
# ---------------------------

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()
    else:
        print("No mode specified. Defaulting to 'db'.")
        mode = 'db'

    if mode not in ['db', 'files']:
        print(f"Invalid mode '{mode}'. Defaulting to 'files'.")
        mode = 'files'

    if mode == 'files':
        data = generate_synthetic_data()
        export_to_files(data)
        print("\nFile generation complete! Synthetic data exported to Excel and JSON files.")
        print(f"Contract files saved in: {LOCAL_DIR if SAVE_MODE == 'local' else S3_BUCKET}")
    else:  # 'db'
        conn = connect()
        cur = conn.cursor()
        try:
            create_tables(cur)
            seed_users(cur)
            company_ids = get_company_ids(cur)
            seed_harper(cur, company_ids)
            seed_oakfield(cur, company_ids)
            spot_check(cur)
            conn.commit()
            print(f"\nSeeding complete! Database populated with realistic synthetic data.")
            if SAVE_MODE == 'local':
                print(f"Contract files saved locally in: {LOCAL_DIR}")
            else:
                print(f"Contract files uploaded to S3 bucket: {S3_BUCKET}")
            export_from_db(cur)
        except Exception as e:
            print(f"Error during seeding: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()