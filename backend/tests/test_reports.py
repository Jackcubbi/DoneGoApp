"""Tests for report CRUD, pagination, PDF download, and stats endpoints."""
import pytest


# ── helpers ───────────────────────────────────────────────────────────────────

def _create_report(client, headers, week=1, year=2026, status="saved"):
    resp = client.post(
        "/api/reports",
        json={
            "week_number": week,
            "year": year,
            "status": status,
            "entries": [
                {"day": "Ma", "hours": "8", "area": "20", "work_code": 1},
                {"day": "Ti", "hours": "6", "area": "15", "work_code": 2},
            ],
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_project(client, headers, name="Testiprojekti"):
    resp = client.post(
        "/api/projects",
        json={"name": name, "project_code": "T001"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── report CRUD ───────────────────────────────────────────────────────────────

def test_create_report(client, auth_headers):
    report = _create_report(client, auth_headers)
    assert report["week_number"] == 1
    assert report["year"] == 2026
    assert report["status"] == "saved"
    assert len(report["entries"]) == 2


def test_list_reports(client, auth_headers):
    _create_report(client, auth_headers, week=5)
    resp = client.get("/api/reports", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_reports_pagination(client, auth_headers):
    for w in range(10, 15):
        _create_report(client, auth_headers, week=w)
    resp = client.get("/api/reports?skip=0&limit=2", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) <= 2


def test_get_report(client, auth_headers):
    report = _create_report(client, auth_headers, week=20)
    resp = client.get(f"/api/reports/{report['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == report["id"]


def test_get_report_not_found(client, auth_headers):
    resp = client.get("/api/reports/999999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_report(client, auth_headers):
    report = _create_report(client, auth_headers, week=30)
    resp = client.put(
        f"/api/reports/{report['id']}",
        json={
            "week_number": 31,
            "year": 2026,
            "entries": [{"day": "Ke", "hours": "7"}],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["week_number"] == 31
    assert len(data["entries"]) == 1


def test_delete_report(client, auth_headers):
    report = _create_report(client, auth_headers, week=40)
    resp = client.delete(f"/api/reports/{report['id']}", headers=auth_headers)
    assert resp.status_code == 204
    resp2 = client.get(f"/api/reports/{report['id']}", headers=auth_headers)
    assert resp2.status_code == 404


def test_reports_isolated_between_users(client, auth_headers):
    """Reports created by one user must not be visible to another."""
    # Register and login a second user
    client.post(
        "/api/register",
        json={"name": "Toinen", "surname": "Käyttäjä", "email": "toinen@example.com", "password": "salasana456"},
    )
    login2 = client.post(
        "/api/login",
        json={"email": "toinen@example.com", "password": "salasana456"},
    )
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    report = _create_report(client, auth_headers, week=50)
    resp = client.get(f"/api/reports/{report['id']}", headers=headers2)
    assert resp.status_code == 404


# ── PDF download ──────────────────────────────────────────────────────────────

def test_download_pdf(client, auth_headers):
    report = _create_report(client, auth_headers, week=2)
    resp = client.get(f"/api/reports/{report['id']}/pdf", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 0


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_summary(client, auth_headers):
    _create_report(client, auth_headers, week=3, status="saved")
    resp = client.get("/api/stats/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_hours" in data
    assert "report_count" in data
    assert data["report_count"] >= 1


def test_stats_by_week(client, auth_headers):
    _create_report(client, auth_headers, week=4, status="saved")
    resp = client.get("/api/stats/by-week", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        assert "label" in data[0]
        assert "hours" in data[0]


def test_stats_by_project(client, auth_headers):
    project = _create_project(client, auth_headers)
    client.post(
        "/api/reports",
        json={"week_number": 6, "year": 2026, "status": "saved", "project_id": project["id"], "entries": [{"day": "Ma", "hours": "4"}]},
        headers=auth_headers,
    )
    resp = client.get("/api/stats/by-project", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_stats_by_workcode(client, auth_headers):
    _create_report(client, auth_headers, week=7, status="saved")
    resp = client.get("/api/stats/by-workcode", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_stats_unauthenticated(client):
    for path in ["/api/stats/summary", "/api/stats/by-week", "/api/stats/by-project", "/api/stats/by-workcode"]:
        assert client.get(path).status_code == 401
