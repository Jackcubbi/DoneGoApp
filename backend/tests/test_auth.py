"""Tests for authentication endpoints: register, login, /me."""
import pytest


def test_register_success(client):
    resp = client.post(
        "/api/register",
        json={
            "name": "Anna",
            "surname": "Mäkinen",
            "email": "anna@example.com",
            "password": "vahvaSalasana1",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "anna@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, registered_user):
    resp = client.post(
        "/api/register",
        json={
            "name": "Toinen",
            "surname": "Henkilö",
            "email": registered_user["email"],
            "password": "toinenSalasana1",
        },
    )
    assert resp.status_code == 400


def test_login_success(client, registered_user):
    resp = client.post(
        "/api/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    resp = client.post(
        "/api/login",
        json={"email": registered_user["email"], "password": "väärä"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/login",
        json={"email": "olematon@example.com", "password": "salasana"},
    )
    assert resp.status_code == 401


def test_me_authenticated(client, auth_headers, registered_user):
    resp = client.get("/api/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == registered_user["email"]
    assert data["name"] == registered_user["name"]


def test_me_unauthenticated(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_me_invalid_token(client):
    resp = client.get("/api/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
