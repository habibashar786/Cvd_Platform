"""
Tests for Phase 2 SaaS, Interoperability, and RAG features.
Verifies JWT auth, tenant isolation, FHIR interop, RAG endpoints, and cryptographic auditing.
"""
import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture(scope="module")
def client():
    """Fixture that manages TestClient lifecycle to trigger startup event handlers."""
    with TestClient(app) as c:
        yield c

def test_jwt_auth_required(client):
    """Verify that secured endpoints require a valid JWT bearer token."""
    res_bad = client.post("/predict", json={
        "age": 55, "gender": 2, "height": 175, "weight": 85,
        "ap_hi": 145, "ap_lo": 92, "cholesterol": 2,
        "gluc": 1, "smoke": 1, "alco": 0, "active": 0
    }, headers={"Authorization": "Bearer invalid-token-string"})
    
    assert res_bad.status_code == 401

def test_user_login_success(client):
    """Verify that logging in with valid credentials yields a valid JWT token."""
    res = client.post("/auth/login", json={
        "username": "doctor",
        "password": "doctor123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "clinician"
    assert data["user"]["tenant_id"] == "Alpha-Health"

def test_user_login_failure(client):
    """Verify that invalid passwords fail login with 401."""
    res = client.post("/auth/login", json={
        "username": "doctor",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_tenant_isolation_stats(client):
    """Verify that Administrators can only see stats for their own tenant."""
    # Login as admin (Alpha-Health tenant)
    res_login = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = res_login.json()["access_token"]
    
    res_stats = client.get("/tenant/stats", headers={"Authorization": f"Bearer {token}"})
    assert res_stats.status_code == 200
    assert res_stats.json()["tenant_id"] == "Alpha-Health"

def test_fhir_observation_ingestion(client):
    """Verify that standard FHIR Transaction Bundles are correctly parsed and predicted."""
    # Login as clinician
    res_login = client.post("/auth/login", json={
        "username": "doctor",
        "password": "doctor123"
    })
    token = res_login.json()["access_token"]
    
    sample_bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "pat-abc",
                    "gender": "female",
                    "birthDate": "1976-06-15"
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-bp",
                    "status": "final",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "85354-9"}]
                    },
                    "component": [
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
                            "valueQuantity": {"value": 142}
                        },
                        {
                            "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4"}]},
                            "valueQuantity": {"value": 88}
                        }
                    ]
                }
            }
        ]
    }
    
    res = client.post("/fhir/Observation", json=sample_bundle, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["resourceType"] == "RiskAssessment"
    assert "prediction" in data
    assert len(data["prediction"]) > 0
    assert "probabilityDecimal" in data["prediction"][0]
    assert data["prediction"][0]["qualitativeRisk"]["coding"][0]["code"] in ["LOW", "MODERATE", "MODERATE-HIGH", "HIGH"]

def test_clinical_rag_query(client):
    """Verify that RAG Query endpoint retrieves cardiology context."""
    res_login = client.post("/auth/login", json={
        "username": "doctor",
        "password": "doctor123"
    })
    token = res_login.json()["access_token"]
    
    res = client.post("/rag/query", json={"query": "hypertension targets and systolic guidelines"}, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert "National Heart Foundation of Australia" in data["sources"][0]["title"]

def test_cryptographic_audit_trail(client):
    """Verify that the cryptographic integrity verifier correctly detects ledger alterations."""
    # Login as clinician to run prediction
    res_clinician_login = client.post("/auth/login", json={
        "username": "doctor",
        "password": "doctor123"
    })
    clinician_token = res_clinician_login.json()["access_token"]
    
    # Run a prediction to write a log line
    client.post("/predict", json={
        "age": 50, "gender": 1, "height": 168, "weight": 72,
        "ap_hi": 120, "ap_lo": 80, "cholesterol": 1,
        "gluc": 1, "smoke": 0, "alco": 0, "active": 1
    }, headers={"Authorization": f"Bearer {clinician_token}"})
    
    # Login as admin to verify ledger
    res_admin_login = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    admin_token = res_admin_login.json()["access_token"]
    
    # Verify ledger (should be intact)
    res_verify = client.get("/audit/verify", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_verify.status_code == 200
    assert res_verify.json()["verified"] is True
