from sqlmodel import create_engine, SQLModel, Session
from .core.config import settings
from pathlib import Path

# Database path
sqlite_file_name = "practice.db"
db_path = settings.BACKEND_DIR / "data" / sqlite_file_name
# Ensure data directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)
sqlite_url = f"sqlite:///{db_path}"

from sqlalchemy import event

engine = create_engine(
    sqlite_url, 
    echo=False, 
    connect_args={"check_same_thread": False, "timeout": 15}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

def seed_data():
    from .models import User, Module
    from passlib.context import CryptContext
    import pandas as pd
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    with Session(engine) as session:
        from sqlmodel import select
        
        # === SEED MODULES (first-run only) ===
        # Only seed modules if none exist - this ensures deleted modules stay deleted
        existing_modules = session.exec(select(Module)).first()
        if not existing_modules:
            modules_csv = settings.BACKEND_DIR / "data" / "modules.csv"
            if modules_csv.exists():
                print("First run: Seeding modules from CSV...")
                df_modules = pd.read_csv(modules_csv)
                for _, row in df_modules.iterrows():
                    module = Module(
                        id=str(row['id']),
                        name=str(row['name']),
                        description=str(row.get('description', '')) if pd.notna(row.get('description')) else ''
                    )
                    session.add(module)
            else:
                # Fallback defaults if no CSV
                print("First run: Seeding default modules...")
                session.add(Module(id="math_stats", name="Math & Stats", description="Basic math and stats practice"))
                session.add(Module(id="python", name="Python", description="Python programming practice"))
        
        # === SEED ADMIN USER ===
        admin = session.exec(select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)).first()
        if not admin:
            print(f"Seeding default admin user: {settings.DEFAULT_ADMIN_USERNAME}")
            admin = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                hashed_password=pwd_context.hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="admin"
            )
            session.add(admin)
        else:
            # Update password just in case
            admin.hashed_password = pwd_context.hash(settings.DEFAULT_ADMIN_PASSWORD)
            session.add(admin)
        
        # Admin user is seeded via DEFAULT_ADMIN_USERNAME/PASSWORD in config/env
            
        session.commit()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    # Auto-migration for missing columns (MUST RUN BEFORE seed_data)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check if user_code exists in userprogress
            result = conn.execute(text("PRAGMA table_info(userprogress)"))
            columns = [row[1] for row in result]
            if columns and "user_code" not in columns:
                print("Migrating schema: Adding user_code to userprogress")
                conn.execute(text("ALTER TABLE userprogress ADD COLUMN user_code TEXT"))
                conn.commit()

            # Check if topic exists in question
            result = conn.execute(text("PRAGMA table_info(question)"))
            columns = [row[1] for row in result]
            if columns and "topic" not in columns:
                print("Migrating schema: Adding topic to question")
                conn.execute(text("ALTER TABLE question ADD COLUMN topic TEXT DEFAULT 'General'"))
                conn.commit()

            # Check if tags exists in question
            result = conn.execute(text("PRAGMA table_info(question)"))
            columns = [row[1] for row in result]
            if columns and "tags" not in columns:
                print("Migrating schema: Adding tags to question")
                conn.execute(text("ALTER TABLE question ADD COLUMN tags TEXT"))
                conn.commit()

            # Check if groq_api_key exists in user
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            if columns and "groq_api_key" not in columns:
                print("Migrating schema: Adding groq_api_key to user")
                conn.execute(text("ALTER TABLE user ADD COLUMN groq_api_key TEXT"))
                conn.commit()
            # Check if has_groq_api_key exists in user
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            if columns and "has_groq_api_key" not in columns:
                print("Migrating schema: Adding has_groq_api_key to user")
                conn.execute(text("ALTER TABLE user ADD COLUMN has_groq_api_key BOOLEAN DEFAULT 0"))
                # Update existing users who have keys
                conn.execute(text("UPDATE user SET has_groq_api_key = 1 WHERE groq_api_key IS NOT NULL AND groq_api_key != ''"))
                conn.commit()

            # Check if openai_api_key exists in user
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            if columns and "openai_api_key" not in columns:
                print("Migrating schema: Adding openai_api_key to user")
                conn.execute(text("ALTER TABLE user ADD COLUMN openai_api_key TEXT"))
                conn.execute(text("ALTER TABLE user ADD COLUMN has_openai_api_key BOOLEAN DEFAULT 0"))
                conn.commit()

            # Check if anthropic_api_key exists in user
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            if columns and "anthropic_api_key" not in columns:
                print("Migrating schema: Adding anthropic_api_key to user")
                conn.execute(text("ALTER TABLE user ADD COLUMN anthropic_api_key TEXT"))
                conn.execute(text("ALTER TABLE user ADD COLUMN has_anthropic_api_key BOOLEAN DEFAULT 0"))
                conn.commit()

            # Check if default_llm_provider exists in user
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            if columns and "default_llm_provider" not in columns:
                print("Migrating schema: Adding default_llm_provider to user")
                conn.execute(text("ALTER TABLE user ADD COLUMN default_llm_provider TEXT DEFAULT 'groq'"))
                conn.commit()
    except Exception as e:
        print(f"Schema migration warning: {e}")

    seed_data()

def get_session():
    with Session(engine) as session:
        yield session
