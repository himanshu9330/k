# SentinelAI-X: System Architecture & Design Specification

## 1. Architectural Overview

SentinelAI-X is an AI-assisted Security Operations Center (SOC) incident response and threat analysis platform designed to process, analyze, score, and remediate cybersecurity events at machine speed.

The platform employs a **tri-tiered hybrid detection and response architecture**:

1. **Deterministic Rule Engine (Layer 1)**: Heuristic pattern matching and signature correlation for zero-latency, highly predictable baseline threat identification.
2. **Generative AI Security Reasoning Engine (Layer 2)**: Large Language Model (Google Gemini via `google-genai` SDK) performing deep forensic contextualization, unstructured pattern deduction, and explainable reasoning.
3. **Deterministic Mathematical Risk Scoring Engine (Layer 3)**: Multi-factor quantitative risk scoring ($0-100$) ensuring mathematical reproducibility, objectivity, and transparent factor explainability.

```
+---------------------------------------------------------------------------------------+
|                                    SENTINELAI-X SOC                                   |
+---------------------------------------------------------------------------------------+
                                           |
                                  [Security Log Stream]
                                           |
                                           v
                        +-------------------------------------+
                        |     1. Secure Ingestion Gateway     |
                        | (Size, MIME, Extension, Traversal)  |
                        +-------------------------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |     2. Multi-Format Log Parser      |
                        |   (SSH, Syslog, Web, JSON, CSV)     |
                        +-------------------------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |    3. Event Normalization Schema    |
                        +-------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
    +-------------------------------+             +-------------------------------+
    | 4. Deterministic Rule Engine  |             |  5. Prompt Injection Defense  |
    | (Brute Force, Spray, Recon)   |             | (Data Boundary Encapsulation) |
    +-------------------------------+             +-------------------------------+
                    |                                             |
                    |           +---------------------+           |
                    +---------->|   6. Google Gemini  |<----------+
                                |  GenAI Intelligence |
                                +---------------------+
                                           |
                                           v (AI Output or Graceful Fallback)
                        +-------------------------------------+
                        | 7. Deterministic Risk Scoring (0-100)|
                        |  (Base + Freq + Priv + Svc + Pat)   |
                        +-------------------------------------+
                                           |
                        +-------------------------------------+
                        |   8. MITRE ATT&CK Matrix Mapping    |
                        |      (T1110, T1046, T1059, etc.)    |
                        +-------------------------------------+
                                           |
                        +-------------------------------------+
                        |  9. Human-in-the-Loop Response Recs |
                        | (Priority, Rationale, Command CLI)  |
                        +-------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                      |                      |
                    v                      v                      v
        +-----------------------+ +------------------+ +----------------------+
        | SQLite / SQLAlchemy   | | Forensic Audit   | | React / TypeScript   |
        | Relational Database   | | Immutable Trail  | | Dark SOC Dashboard   |
        +-----------------------+ +------------------+ +----------------------+
```

---

## 2. Component Specifications

### 2.1 Secure Log Ingestion (`backend/routes/log_routes.py`)
- **Input Formats**: `.log`, `.txt`, `.json`, `.csv`.
- **Validation Controls**:
  - Filename sanitization via `os.path.basename` to prevent directory traversal attacks.
  - Strict file extension validation (`.log`, `.txt`, `.json`, `.csv`).
  - Size enforcement: Maximum upload ceiling of 10 MB (`MAX_UPLOAD_SIZE_BYTES`).
  - Empty file detection.

### 2.2 Multi-Format Log Parser (`backend/services/parser_service.py`)
Extracts telemetry attributes into a strongly-typed normalized schema:
- `timestamp`: Extracted ISO/syslog timestamp or `None`.
- `event_type`: Classified event (`failed_login`, `successful_login`, `privileged_command_execution`, `web_request`).
- `source_ip`: Attacker / client IPv4/IPv6 address.
- `destination_ip`: Target host IP.
- `username`: Target or acting user account.
- `service`: Network protocol (`ssh`, `rdp`, `sudo`, `http`, `database`).
- `port`: Destination port number.
- `status`: Outcome (`failed`, `accepted`, `executed`).
- `raw_log`: Immutable raw line preserved as forensic evidence.

### 2.3 Standalone Deterministic Rule Engine (`backend/services/detection_service.py`)
- Evaluates multi-event streams across correlation windows:
  - **Port Scanning Reconnaissance (`RULE_PORT_SCAN_RECON`)**: Single source IP targeting $\ge 4$ distinct destination ports. Severity: `MEDIUM`.
  - **Password Spraying (`RULE_PASSWORD_SPRAY_DETECTION`)**: Single source IP attempting logins across $\ge 3$ distinct accounts. Severity: `HIGH`.
  - **Brute Force Attack (`RULE_BRUTE_FORCE_VELOCITY`)**: Single source IP generating $\ge 3$ failed authentication attempts. Severity: `HIGH`.
  - **Privilege Escalation (`RULE_PRIVILEGE_ESCALATION_COMMAND`)**: Unauthorized invocation of sensitive binaries (`cat /etc/shadow`, `chmod 777 /etc/passwd`). Severity: `CRITICAL`.
  - **Web Exploitation (`RULE_WEB_EXPLOITATION_SIGNATURE`)**: SQL injection or directory traversal signatures. Severity: `HIGH`.

### 2.4 Hardened Generative AI Service (`backend/services/gemini_service.py`)
- Uses Google's official `google-genai` SDK v2.
- Dynamic model selection via `GEMINI_MODEL` (defaults to `gemini-3.6-flash`).
- **Prompt Injection Defense**:
  - Untrusted log streams are strictly isolated within boundary markers (`<<<UNTRUSTED_SECURITY_LOG_DATA_START>>>` ... `<<<UNTRUSTED_SECURITY_LOG_DATA_END>>>`).
  - Strict system prompt rules instructing Gemini to treat logs as passive data, never execute overrides, and never expose secrets.
- **Pydantic Response Validation**: Strict schema enforcement on AI output.
- **Graceful Fallback**: If Gemini is offline, throttled, or returns malformed JSON, the platform seamlessly substitutes the deterministic rule engine analysis, setting `ai_status: FALLBACK` without service disruption.

### 2.5 Deterministic Risk Scoring Engine (`backend/services/risk_service.py`)
Calculates an objective risk score $R \in [0, 100]$:

$$\text{Risk Score} = \min\left(100, S_{\text{base}} + F_{\text{attempts}} + P_{\text{privilege}} + V_{\text{service}} + T_{\text{pattern}} + C_{\text{confidence}}\right)$$

| Component | Weight Range | Scoring Logic |
| :--- | :--- | :--- |
| **Base Severity ($S_{\text{base}}$)** | 10 – 50 pts | LOW = 10, MEDIUM = 25, HIGH = 40, CRITICAL = 50 |
| **Frequency ($F_{\text{attempts}}$)** | 0 – 25 pts | $\ge 10$ attempts = +25, $\ge 5$ = +20, $\ge 3$ = +15, $\ge 1$ = +5 |
| **Privileged Target ($P_{\text{privilege}}$)** | 0 – 15 pts | Targets `root`, `admin`, `administrator`, `system`, `dbadmin` = +15 |
| **Sensitive Service ($V_{\text{service}}$)** | 0 – 10 pts | Targets `ssh`, `rdp`, `smb`, `database`, `vnc` = +10; `ftp`, `ldap` = +8 |
| **Attack Pattern ($T_{\text{pattern}}$)** | 0 – 10 pts | Matched credential brute force, port scan, privilege escalation = +10 |
| **Confidence ($C_{\text{confidence}}$)** | 0 – 5 pts | Corroborating telemetry confidence $\ge 0.85$ = +5, $\ge 0.60$ = +3 |

**Classification Tiers**:
- $0 - 29$: **LOW**
- $30 - 59$: **MEDIUM**
- $60 - 79$: **HIGH**
- $80 - 100$: **CRITICAL**

### 2.6 MITRE ATT&CK Framework Service (`backend/services/mitre_service.py`)
Maps observed evidence to MITRE Enterprise matrix techniques:
- `T1110`: Brute Force (Credential Access)
- `T1110.001`: Password Guessing
- `T1110.003`: Password Spraying
- `T1046`: Network Service Discovery / Port Scanning (Discovery)
- `T1078`: Valid Accounts (Initial Access / Defense Evasion)
- `T1059`: Command and Scripting Interpreter (Execution)
- `T1021`: Remote Services (Lateral Movement)
- `T1190`: Exploit Public-Facing Application (Initial Access)
- `T1003`: OS Credential Dumping (Credential Access)

### 2.7 Incident Response Recommendation Engine (`backend/services/response_service.py`)
- Synthesizes actionable defensive countermeasures.
- **Strict Human-in-the-Loop (HITL) Model**:
  - Actions are proposed with priority ratings (`P1`-`P4`), operational risk levels (`LOW`, `MEDIUM`, `HIGH`), and CLI command preview templates.
  - The system **never** executes destructive commands (firewall changes, account locks, system isolation) automatically.

### 2.8 Forensic Audit Logging (`backend/services/audit_service.py`)
- Maintains an append-only audit trail in the relational database.
- Records all actions (`LOG_INGESTION`, `STATUS_CHANGE`, `RESPONSE_APPROVAL`, `USER_LOGIN`).
- Automatically masks passwords, tokens, API keys, and secret hashes.

---

## 3. Database Entity Relationship Diagram

```
+----------------+       1:N       +-------------------+
|  SecurityLog   | --------------< |   SecurityEvent   |
+----------------+                 +-------------------+
        |
        | 1:N
        v
+----------------+       1:1       +-------------------+
|    Incident    | --------------  |  RiskAssessment   |
+----------------+                 +-------------------+
        |
        +-- 1:N --> +-------------------+
        |           |  ResponseAction   |
        |           +-------------------+
        |
        +-- N:1 --> +-------------------+
                    |  MitreTechnique   |
                    +-------------------+
```
