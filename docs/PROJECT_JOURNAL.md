# SentinelAI-X: Project Development Journal

This journal documents the chronological engineering milestones, architectural decisions, and verification steps taken during the development of SentinelAI-X.

---

## Session 1 — Initial Project Inspection & Architecture Design
- **Date**: August 2026
- **Activities**:
  - Inspected existing repository structure (`main.py`, `log_parser.py`, `gemini_service.py`, `risk_engine.py`).
  - Identified working foundation: FastAPI backend, basic SSH regex parser, `google-genai` integration, prototype risk calculation.
  - Formulated 12-phase master implementation roadmap spanning multi-factor risk scoring, SQLite/SQLAlchemy relational models, MITRE ATT&CK mapping, prompt injection armor, human-in-the-loop response recommendations, SOC dashboard APIs, React/TypeScript frontend, automated pytest suite, and academic documentation.
  - Created initial plan artifact and obtained user approval.

---

## Session 2 — Phase 1: Deterministic Risk Scoring Engine
- **Module**: `backend/services/risk_service.py` & `backend/services/risk_engine.py`
- **Accomplishments**:
  - Implemented reproducible mathematical formula ($0 - 100$):
    $$\text{Risk Score} = \min(100, S_{\text{base}} + F_{\text{attempts}} + P_{\text{privilege}} + V_{\text{service}} + T_{\text{pattern}} + C_{\text{confidence}})$$
  - Added granular 6-factor breakdown dictionary for full explainability on the SOC dashboard.
  - Maintained backwards compatibility via `services/risk_engine.py` re-export.
  - Tested calculation against sample brute force scenarios (Score: 95, CRITICAL).

---

## Session 3 — Phase 2: Relational Database & Incident Entity Schema
- **Module**: `backend/app/database.py`, `backend/models/*`, `backend/schemas/*`
- **Accomplishments**:
  - Established SQLite engine with SQLAlchemy 2.0 ORM models:
    - `User`: RBAC user accounts (`ADMIN`, `ANALYST`, `VIEWER`)
    - `SecurityLog`: Ingested log files and raw content
    - `SecurityEvent`: Normalized security event telemetry
    - `Incident`: Core SOC unit with unique ID generation (`INC-000001`) and lifecycle states (`OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`, `FALSE_POSITIVE`)
    - `RiskAssessment`: Mathematical score breakdown persistence
    - `MitreTechnique`: MITRE ATT&CK matrix knowledgebase
    - `ResponseAction`: Prioritized defensive countermeasure proposals
    - `AuditLog`: Immutable forensic audit trail
  - Created corresponding Pydantic schemas with standardized API response wrappers (`ApiResponse[T]`, `ApiErrorResponse`).

---

## Session 4 — Phase 3: MITRE ATT&CK Enterprise Matrix Service
- **Module**: `backend/services/mitre_service.py`
- **Accomplishments**:
  - Embedded canonical MITRE enterprise knowledgebase with technique IDs (T1110, T1110.001, T1110.003, T1046, T1078, T1059, T1021, T1190, T1003).
  - Built automated database seeder and rule-based heuristic resolution linking observed telemetry to techniques.

---

## Session 5 — Phase 4: Incident Response Recommendation Engine
- **Module**: `backend/services/response_service.py`
- **Accomplishments**:
  - Synthesized defensive countermeasures (IP blocking, password resets, SSH hardening, Fail2Ban).
  - Built strict Human-in-the-Loop approval model: All actions are created with `status: PROPOSED` and CLI command previews. Zero autonomous destructive execution.

---

## Session 6 — Phase 5: Multi-Format Parser & Rule-Based Threat Detection
- **Module**: `backend/services/parser_service.py` & `backend/services/detection_service.py`
- **Accomplishments**:
  - Developed multi-format parser supporting SSH auth logs, Linux syslog, Web access logs, JSON (single and NDJSON), and CSV logs.
  - Built standalone deterministic detection engine covering port scanning, password spray, brute force velocity, privilege escalation commands, and web exploitation.

---

## Session 7 — Phase 6: Hardened Generative AI Service
- **Module**: `backend/services/gemini_service.py`
- **Accomplishments**:
  - Implemented dynamic model configuration (`GEMINI_MODEL`, default: `gemini-3.6-flash`).
  - Added lazy client initialization to prevent import crashes in offline test environments.
  - Built prompt injection defense using boundary tokens (`<<<UNTRUSTED_SECURITY_LOG_DATA_START>>>` ... `<<<UNTRUSTED_SECURITY_LOG_DATA_END>>>`).
  - Added Pydantic schema validation on Gemini JSON outputs.
  - Implemented seamless deterministic fallback: When Gemini is offline or returns invalid JSON, the platform produces a complete valid incident report from the rule engine.

---

## Session 8 — Phase 7: Authentication, RBAC & Forensic Audit Logging
- **Module**: `backend/services/auth_service.py` & `backend/services/audit_service.py`
- **Accomplishments**:
  - Implemented bcrypt password hashing and JWT access token issuance.
  - Enforced Role-Based Access Control (`ADMIN`, `ANALYST`, `VIEWER`).
  - Built immutable forensic audit logger with automated redaction of sensitive credentials.

---

## Session 9 — Phase 8: REST API Routes & Orchestration
- **Module**: `backend/routes/*`, `backend/main.py`
- **Accomplishments**:
  - Implemented modular routers: `/api/auth`, `/api/logs`, `/api/incidents`, `/api/dashboard`, `/api/mitre`, `/api/audit`.
  - Configured CORS middleware, lifecycle database startup & seeding, and global exception handlers.
  - Preserved root `/`, `/health`, and legacy `/upload-log` endpoints for backwards compatibility.

---

## Session 10 — Phase 9: React + TypeScript + Vite SOC Frontend
- **Module**: `frontend/`
- **Accomplishments**:
  - Scaffolded React 18 + TypeScript + Vite + Tailwind CSS SOC application.
  - Built cybersecurity dark theme with glow borders, radial risk meter, KPI cards, interactive incident feed, deep-dive inspection page, MITRE ATT&CK matrix explorer, printable executive briefings, and audit trail viewer.
  - Verified compilation: `npm run build` completed with 0 errors in 4.97s.

---

## Session 11 — Phase 10: Automated Test Suite & Verification
- **Module**: `backend/tests/*`
- **Accomplishments**:
  - Created 24 unit, integration, and security tests covering parser, rule engine, risk scoring, MITRE mapping, Gemini mocked success, malformed fallback, incident workflow, prompt injection defense, and authentication.
  - Executed `pytest`: **24 passed, 100% success rate**.

---

## Session 12 — Phase 11: Documentation & Final Polish
- **Module**: `README.md`, `docs/ARCHITECTURE.md`, `docs/API_DOCUMENTATION.md`, `docs/SECURITY.md`, `docs/THREAT_MODEL.md`, `docs/PROJECT_JOURNAL.md`, `.env.example`.
- **Accomplishments**:
  - Authored comprehensive academic-grade documentation satisfying all MCA final-year criteria and real-world cybersecurity SOC product requirements.
