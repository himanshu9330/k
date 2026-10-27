# SentinelAI-X: REST API Documentation

Base URL: `http://localhost:8000/api`

Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`

---

## 1. Response Standards

### Success Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": null
  }
}
```

---

## 2. API Endpoints

### 2.1 Authentication & Profile

#### Register User
`POST /api/auth/register`
- **Request Body**:
```json
{
  "username": "analyst_sarah",
  "email": "sarah@sentinelai.io",
  "password": "SecurePassword123!",
  "full_name": "Sarah Connor",
  "role": "ANALYST"
}
```
- **Response**: `200 OK` with user profile object.

#### Login User
`POST /api/auth/login`
- **Request Body**:
```json
{
  "username": "analyst_sarah",
  "password": "SecurePassword123!"
}
```
- **Response**: `200 OK` with JWT access token.

#### Get Current Profile
`GET /api/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` with authenticated user profile.

---

### 2.2 Security Log Ingestion

#### Ingest & Analyze Security Log
`POST /api/logs/upload`
- **Content-Type**: `multipart/form-data`
- **Form Data**: `file` (Binary payload: `.log`, `.txt`, `.json`, `.csv`, max 10MB)
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "log_id": 1,
    "filename": "sample_security.log",
    "file_size": 366,
    "log_format": "syslog_ssh",
    "event_count": 5,
    "incident_id": "INC-000001",
    "risk_score": 95,
    "risk_level": "CRITICAL",
    "ai_status": "COMPLETED"
  },
  "message": "Log parsed and analyzed successfully."
}
```

#### List Uploaded Logs
`GET /api/logs?page=1&page_size=20`
- **Response**: `200 OK` with paginated list of ingested logs.

#### Get Log Details
`GET /api/logs/{id}`
- **Response**: `200 OK` with log metadata and normalized security events.

---

### 2.3 Incident Management

#### List Incidents
`GET /api/incidents?severity=HIGH&status=OPEN&search=192.168.1.15&page=1&page_size=20`
- **Query Parameters**: `severity`, `status`, `incident_type`, `source_ip`, `target_service`, `mitre_technique`, `search`, `page`, `page_size`.
- **Response**: `200 OK` with list of `IncidentResponse` objects.

#### Get Incident Details
`GET /api/incidents/{incident_id}`
- **Response**: `200 OK` with deep-dive incident object, risk assessment factor breakdown, MITRE ATT&CK card, response recommendations, and evidence events.

#### Update Incident Lifecycle Status
`PATCH /api/incidents/{incident_id}/status`
- **Request Body**:
```json
{
  "status": "INVESTIGATING",
  "notes": "Analyst commenced threat actor IP triage."
}
```
- **Allowed Statuses**: `OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`, `FALSE_POSITIVE`.

#### Approve / Reject Response Action
`POST /api/incidents/{incident_id}/response-actions/{action_id}/status`
- **Request Body**:
```json
{
  "status": "APPROVED"
}
```
- **Allowed Statuses**: `APPROVED`, `REJECTED`, `EXECUTED`.

#### Generate Executive Incident Briefing Report
`GET /api/incidents/{incident_id}/report`
- **Response**: `200 OK` with structured executive report.

---

### 2.4 SOC Dashboard & Analytics

#### Dashboard Summary KPI Metrics
`GET /api/dashboard/summary`
- **Response**: Total incidents, severity breakdown, status breakdown, average risk score, total events, pending response actions, recent alerts.

#### Attack Type Distribution
`GET /api/dashboard/attacks`

#### MITRE ATT&CK Frequency
`GET /api/dashboard/mitre`

#### Top Attacking Source IPs
`GET /api/dashboard/top-sources`

#### Targeted Services
`GET /api/dashboard/top-targets`

---

### 2.5 MITRE ATT&CK Matrix

#### List All Techniques
`GET /api/mitre`

#### Technique Lookup
`GET /api/mitre/{technique_id}` (e.g. `GET /api/mitre/T1110`)

---

### 2.6 Forensic Audit Trail

#### Query Audit Logs
`GET /api/audit?action=LOG_INGESTION_AND_INCIDENT_CREATION&search=INC-000001&page=1&page_size=50`
