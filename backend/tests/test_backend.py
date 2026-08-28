import os
import pytest
import requests

BASE_URL = "https://8543c06b-ba8e-4866-97cc-a7adc4679f14.preview.emergentagent.com"


class TestHealth:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=15)
        assert r.status_code == 200
        assert r.json().get("status") == "healthy"

    def test_root(self):
        r = requests.get(f"{BASE_URL}/api/", timeout=15)
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


class TestContact:
    def test_contact_valid(self):
        payload = {
            "name": "TEST_Reviewer",
            "email": "test_reviewer@example.com",
            "subject": "TEST subject from automated tests",
            "message": "This is an automated test message. Please ignore.",
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("status") == "success"
        assert "sent" in data.get("message", "").lower()

    def test_contact_honeypot(self):
        payload = {
            "name": "TEST_Bot",
            "email": "bot@example.com",
            "subject": "spam",
            "message": "spam message",
            "website": "http://spam.example.com",
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
        # Silently accepted, no email sent
        assert r.status_code == 200
        assert r.json().get("status") == "success"

    def test_contact_missing_email(self):
        payload = {
            "name": "TEST_NoEmail",
            "subject": "s",
            "message": "hi",
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
        assert r.status_code == 422

    def test_contact_invalid_email(self):
        payload = {
            "name": "TEST_BadEmail",
            "email": "not-an-email",
            "subject": "s",
            "message": "hi",
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
        assert r.status_code == 422

    def test_contact_empty_message(self):
        payload = {
            "name": "TEST_Empty",
            "email": "e@example.com",
            "subject": "s",
            "message": "",
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload, timeout=15)
        assert r.status_code == 422
