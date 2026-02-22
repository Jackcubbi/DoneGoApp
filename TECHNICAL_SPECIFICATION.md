# TECHNICAL SPECIFICATION

## Work Time and Piecework Tracking System

### Project: DoneGo / Urakka Work Tracker

---

## 1. General Information

**Project Name:** DoneGo / Urakka Work Tracker

**Application Type:** Web application for tracking work hours and completed piecework tasks.

**Project Goal:**
Create a system that allows workers to:

- fill in weekly work reports
- record hours and type of work performed (m2/€, meters/€, etc.)
- automatically generate a PDF report
- send the report to a work chat (WhatsApp)

**Runtime Environment:** Docker

---

## 2. System Users

### 2.1 Worker

The primary user of the system.

**Functions:**

- registration
- login
- create a weekly report
- select the type of work performed
- add custom work types
- save a report
- generate PDF
- send a report

---

### 2.2 Administrator (optional)

Additional role for system management.

**Functions:**

- view all reports
- manage users
- view statistics
- monitor sent reports

---

## 3. Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy (ORM)
- SQLite (for MVP)
- JWT authentication
- Bcrypt (password hashing)

**PDF Generation:**

- WeasyPrint

**Integration:**

- Twilio WhatsApp API

---

### Frontend

- Vue 3
- Vite
- Pinia (state management)
- Axios (API communication)
- SCSS (styling)

**UI Components:**

- TailwindCSS (optional)

---

### Infrastructure

- Docker
- Docker Compose

---

## 4. System Architecture

```
Frontend (Vue)
      ↓
  REST API
      ↓
Backend (FastAPI)
      ↓
Database (SQLite)
      ↓
PDF Generator
      ↓
WhatsApp API
```

---

## 5. Core Functionality

### 5.1 User Registration

Users must be able to create an account.

**Registration fields:**

- First name
- Last name
- Email
- Phone
- Password

After registration the user gains access to their personal dashboard.

---

### 5.2 Authentication

Authentication is performed using:

- Email
- Password

JWT token system is used.

---

### 5.3 Personal Dashboard

After login the user lands on the Dashboard.

**Displayed:**

- current week
- list of recent reports
- button to create a new report

**Interface sections:**

- Profile
- Weekly Reports
- Create Report
- Sent Reports

---

## 6. Weekly Report

The user fills in a table with working days.

**Example:**

| Day | Hours    | Work Code |
| --- | -------- | --------- |
| Ma  | -        | -         |
| Ti  | -        | -         |
| Ke  | -        | -         |
| To  | 21/22/23 | 1         |
| Pe  | 24/25    | 1         |

### Week Numbering

The week number is determined automatically based on the calendar.

**Example:**

- Week 10
- Week 11
- Week 12

The user can also select a different week manually.

---

## 7. Work Types (Work Codes)

The system contains a list of standard work types.

| Code | Description                 |
| ---- | --------------------------- |
| 1    | Jalkojen poraus             |
| 2    | Rungon asennus ja suoristus |
| 3    | Villan asennus              |
| 4    | Kipsilevyjen asennus        |

### Custom Work Types

The user can:

- add a new work code
- edit a work code
- delete a work code

**Example:**

```
5 = Maalaus
6 = Purku
```

---

## 8. Creating a Report

The user:

1. selects the week number
2. fills in the table
3. clicks the **Save** or **Send** button

---

## 9. PDF Generation

After clicking the "Send" button the system generates a PDF file.

**Example PDF structure:**

```
URAKKATYÖ – VIIKKO RAPORTTI

Työntekijä: Eduard Bolsakov
Viikko: 10

Ma | -        | -
Ti | -        | -
Ke | -        | -
To | 21/22/23 | 1
Pe | 24/25    | 1

Työvaihe:
1 = Jalkojen poraus
2 = Rungon asennus ja suoristus
3 = Villan asennus
4 = Villan asennus
```

---

## 10. Sending a Report

After the PDF is generated the report is automatically sent to the work chat.

**Primary channel:** WhatsApp group.

**Used:** Twilio WhatsApp API.

---

## 11. Database Structure

### Table `Users`

| Field         | Type     |
| ------------- | -------- |
| id            | INTEGER  |
| name          | VARCHAR  |
| surname       | VARCHAR  |
| email         | VARCHAR  |
| phone         | VARCHAR  |
| password_hash | VARCHAR  |
| created_at    | DATETIME |

### Table `WorkCodes`

| Field       | Type    |
| ----------- | ------- |
| id          | INTEGER |
| code        | INTEGER |
| description | VARCHAR |
| user_id     | INTEGER |

### Table `WeeklyReports`

| Field       | Type     |
| ----------- | -------- |
| id          | INTEGER  |
| user_id     | INTEGER  |
| week_number | INTEGER  |
| year        | INTEGER  |
| status      | VARCHAR  |
| created_at  | DATETIME |

> status: `draft` / `sent`

### Table `WorkEntries`

| Field     | Type    |
| --------- | ------- |
| id        | INTEGER |
| report_id | INTEGER |
| day       | VARCHAR |
| hours     | VARCHAR |
| work_code | INTEGER |

---

## 12. Backend API

### Auth API

```
POST /api/register
POST /api/login
```

### Reports API

```
GET    /api/reports
POST   /api/reports
GET    /api/reports/{id}
PUT    /api/reports/{id}
POST   /api/reports/{id}/send
```

### Work Codes API

```
GET    /api/workcodes
POST   /api/workcodes
PUT    /api/workcodes/{id}
DELETE /api/workcodes/{id}
```

---

## 13. User Interface

### Dashboard

Displays:

- current week
- recent reports
- button to create a report

### Report Page

**Table:**

| Päivä | Tunnit | Työvaihe |
| ----- | ------ | -------- |

**Buttons:**

- Save
- Send
- Download PDF

---

## 14. Security

- JWT authentication
- Bcrypt password hashing
- access rights verification
- protection against access to other users' reports

---

## 15. Development Stages

### Stage 1 — MVP

- user registration
- authentication
- personal dashboard
- create a weekly report
- save a report
- PDF generation

### Stage 2

- send report via WhatsApp
- custom work types
- report list

### Stage 3

- mobile version
- analytics
- work photo upload
- report signing

---

## 16. Potential Future Improvements

- mobile application
- Excel export
- accounting system integration
- photo documentation of completed work
- manager report approval system

---

## 17. Development Estimate

**Recommended MVP development timeframe:** 4–6 weeks.

**Expected outcome:**
A fully functional work time tracking system with automatic PDF report generation and WhatsApp delivery.
