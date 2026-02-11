import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
from pgvector.sqlalchemy import Vector

from app.main import app
from app.db.session import get_db
from app.models.base import Base
from app.services.llm_service import llm_service

# --- FIX FOR SQLITE COMPATIBILITY ---
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON, String

from sqlalchemy.ext.compiler import compiles

# 1. Map PostgreSQL UUID -> SQLite String
@compiles(UUID, "sqlite")
def compile_uuid(type_, compiler, **kw):
    return "VARCHAR"

# 2. Map PostgreSQL Vector -> SQLite JSON
@compiles(Vector, "sqlite")
def compile_vector(type_, compiler, **kw):
    return "JSON"
# ------------------------------------

from sqlalchemy.pool import StaticPool

# Setup Isolated Test Database (In-Memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    """
    Creates a fresh database for the test session.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db_session):
    """
    FastAPI Test Client with dependency overrides.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def mock_llm():
    """
    Mocks the LLM Service so we don't hit OpenAI during tests.
    """
    mock_response = """{
        "type": "analysis_response",
        "title": "Product B Analysis",
        "blocks": [
            { "type": "summary", "text": "Product B sales are down due to pricing." },
            { "type": "metrics", "items": [ { "label": "Revenue", "value": "£0.8m", "change": "-24%" } ] },
            { "type": "recommended_action", "title": "Approve Subscription", "text": "Projected ROI: £0.9m", "cta": { "label": "Approve", "target": "decision_inbox" } }
        ]
    }"""
    
    # Save original method
    original_stream = llm_service.stream_chat
    
    # Mock
    llm_service.stream_chat = MagicMock(return_value=iter([mock_response]))
    
    yield llm_service
    
    # Restore
    llm_service.stream_chat = original_stream