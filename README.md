# ☁️ AWS Technical Support RAG Assistant & ML Classification Engine

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-Flask%20%2F%20Vercel%20WSGI-000000?logo=vercel&logoColor=white)](https://vercel.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%208.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Model Classification](https://img.shields.io/badge/Model%20Inference-1.33%20ms%20%28100%25%20Acc%29-FF9900?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Vector Store](https://img.shields.io/badge/Vector%20Store-ChromaDB%20Persistent-red?logo=cache&logoColor=white)](https://www.trychroma.com/)
[![Test Suite](https://img.shields.io/badge/Tests-33%2F33%20Passing-brightgreen?logo=pytest&logoColor=white)](https://pytest.org/)
[![Deployment](https://img.shields.io/badge/Deployment-Vercel%20%26%20Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**An enterprise-grade, domain-specific Retrieval-Augmented Generation (RAG) assistant and sub-millisecond machine learning classifier designed for Amazon Web Services (AWS) Cloud infrastructure support.**

[Live Architecture](#-system-architecture) • [Key Features](#-key-features) • [Quickstart Guide](#-quickstart-guide) • [IntelliJ & IDE Setup](#-intellij-idea--ide-setup) • [Vercel Deployment](#-vercel-deployment) • [API Reference](#-api-endpoints)

</div>

---

## 📌 Executive Summary

Generic Large Language Models frequently suffer from hallucinations when diagnosing technical cloud incidents—inventing non-existent CLI flags, generating invalid IAM policies, or returning conflicting troubleshooting advice. In production cloud operations, bad guidance leads to downtime, configuration drift, and critical security vulnerabilities.

The **AWS Technical Support Assistant** solves this through a multi-tiered architecture:
1. **Ultra-Fast Model Classifier (< 1.5 ms)**: Accepts and evaluates incoming queries across all technical categories (`TROUBLESHOOTING`, `CONFIGURATION_SETUP`, `CLI_SCRIPT_GENERATION`, `SECURITY_BEST_PRACTICE`, `CONCEPTUAL_EXPLANATION`, `GREETING`, `OUT_OF_SCOPE`) with **100.0% accuracy**.
2. **Friendly & Conversational Persona**: Greets users warmly (*"Hello! I'd be glad to help you resolve this..."*), answers conversational inquiries naturally, and delivers exact, step-by-step technical solutions without boilerplate or extraneous meta-commentary.
3. **Sub-30ms Semantic Retrieval (ChromaDB)**: Searches authoritative AWS documentation chunks embedded via `all-MiniLM-L6-v2` with cosine distance thresholding.
4. **Relational MySQL 8.0 Persistence**: Centralized relational storage for user accounts, bcrypt-hashed credentials, chat sessions, prompt-response history, latency metrics, and security audit logs.
5. **Zero-Friction Deployment**: Fully optimized for **Vercel** serverless hosting (`vercel.json`, `api/index.py`, `public/`) and containerized **Docker Compose** orchestration.

---

## 🏗️ System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                    USER INTERFACE                                     |
|                  Vercel Static Web Client (public/index.html & app.js)                |
|           • User Authentication (Login/Register/1-Click Demo)                         |
|           • Real-Time ML Classification Pills (Intent, Service, Urgency, Latency)      |
|           • Conversational Chat Stream & Interactive Markdown + Code Rendering        |
+-------------------------------------------+-------------------------------------------+
                                            |
                                  HTTPS / REST JSON API
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                          BACKEND APPLICATION ENGINE (api/index.py)                    |
|                        Vercel Serverless / Flask WSGI Controller                      |
+-------------------------------------------+-------------------------------------------+
                     |                      |                      |
                     v                      v                      v
    +--------------------------------+ +------------------+ +---------------------------+
    | Trained ML Intent Classifier   | | Live MySQL 8.0   | | Domain-Specific RAG       |
    | (src/models/intent_classifier) | | Relational DB    | | Pipeline (src/rag)        |
    | • TF-IDF + Logistic Regression | | (127.0.0.1:3307) | | • Semantic Retrieval      |
    | • Latency: ~1.33 ms            | | • `users`        | |   (ChromaDB Vector Store)   |
    | • Accuracy: 100.0%             | | • `chat_history` | | • Cosine Filtering        |
    | • Fast Guardrails (< 5 ms)     | | • `audit_logs`   | | • Anti-Hallucination      |
    +--------------------------------+ +------------------+ |   Prompt Grounding        |
                                                            | • Exact Solution Matcher  |
                                                            +---------------------------+
```

---

## ⚡ Key Features

| Capability | Technical Implementation | Benefit |
| :--- | :--- | :--- |
| **Sub-Millisecond Classification** | Scikit-Learn TF-IDF N-Gram Vectorizer + Balanced Logistic Regression | Categorizes user intent, service, and urgency in **~1.33 ms** before hitting retrieval. |
| **Friendly & Engaging Persona** | Specialized `GREETING` intent & conversational framing | Interacts politely (*"Hello!"*, *"You're welcome!"*), keeping tone friendly while providing direct technical fixes. |
| **Exact Solution Matcher** | Vectorized Exact Solution Model (`src/models/solution_model.py`) | Instantly maps known technical failure patterns to exact AWS remedies with code blocks. |
| **Domain-Specific RAG** | ChromaDB with `sentence-transformers/all-MiniLM-L6-v2` | Retrieves ground-truth documentation across Amazon EC2, Amazon S3, AWS Lambda, and AWS IAM. |
| **MySQL 8.0 Relational Layer** | PyMySQL connection pool (`schema.sql`) | Persistent storage for users, sessions, conversation logs, and security audit events. |
| **Enterprise Security** | Bcrypt password hashing (12 rounds) + parameterized queries | Prevents SQL injection, secures credentials, and logs all authentication attempts with IP tracing. |
| **Vercel-Ready Architecture** | Modular Flask WSGI routing + decoupled `public/` frontend | Deployable instantly to Vercel without complex container configuration. |
| **Exhaustive Test Suite** | 33 automated tests across unit, auth, DB, model, and pipeline | Verified 100% test pass rate with Pytest. |

---

## 🎯 Model Training & Evaluation Metrics

The classification engine (`src/models/intent_classifier.py`) evaluates requests across **7 distinct intents** and **6 domain categories**:

```text
=================================================================
      AWS TECHNICAL SUPPORT MODEL TRAINING & EVALUATION REPORT
=================================================================
Model Architecture       : TFIDF_LogisticRegression_Ensemble
Training Sample Count    : 92
Intent Classification Acc: 100.00%
Service Identification   : 100.00%
Urgency Classification   : 100.00%
Average Inference Latency: 1.33 ms
Recognized Intents       : CLI_SCRIPT_GENERATION, CONCEPTUAL_EXPLANATION, 
                           CONFIGURATION_SETUP, GREETING, OUT_OF_SCOPE, 
                           SECURITY_BEST_PRACTICE, TROUBLESHOOTING
Recognized Services      : Amazon EC2, Amazon S3, AWS Lambda, AWS IAM, 
                           General AWS, Out-of-Scope
=================================================================
```

### Supported Intent Taxonomy
- **`GREETING`**: Welcoming messages (*"Hello"*, *"Hi"*, *"How are you"*, *"Who are you"*, *"Thank you"*, *"Goodbye"*).
- **`TROUBLESHOOTING`**: Diagnosing runtime errors (*"EC2 Permission denied"*, *"S3 NoSuchBucket"*, *"Lambda timeout"*).
- **`CONFIGURATION_SETUP`**: Setup procedures (*"Configure S3 lifecycle to Glacier"*, *"Attach IAM role to EC2"*).
- **`CLI_SCRIPT_GENERATION`**: AWS CLI and SDK scripts (*"aws s3 sync command"*, *"describe EC2 instances"*).
- **`SECURITY_BEST_PRACTICE`**: Hardening infrastructure (*"Principle of Least Privilege"*, *"Block S3 Public Access"*).
- **`CONCEPTUAL_EXPLANATION`**: Architectural trade-offs (*"t3 burstable vs c5 compute optimized instances"*).
- **`OUT_OF_SCOPE`**: Non-AWS topics (*"Azure VMs"*, *"GCP BigQuery"*, *"Banana bread recipes"* — rejected in < 5 ms).

---

## 🗄️ MySQL Database Architecture

All user accounts, sessions, chats, and audit trails are persisted in MySQL:

```sql
-- Schema Summary (schema.sql)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    query TEXT NOT NULL,
    response MEDIUMTEXT NOT NULL,
    intent VARCHAR(50),
    service VARCHAR(50),
    urgency VARCHAR(20),
    is_grounded TINYINT(1),
    latency_ms FLOAT,
    sources_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python**: Version 3.10 to 3.14
- **MySQL**: Local MySQL / XAMPP on port `3307` or `3306`

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd "An AI Assistant for Technical Support"

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your database parameters match your environment:
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=aws_support_rag
DB_FALLBACK_SQLITE=false

# Optional LLM Key (defaults to high-speed demo mode if omitted)
OPENAI_API_KEY=
LLM_PROVIDER=demo
```

### 4. Train Model & Initialize Database
```bash
# Train the ML Intent & Solution Classifier
python scripts/train_model.py

# Initialize MySQL tables and default users
python scripts/init_mysql.py
```

### 5. Launch the Web Application
```bash
python api/index.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 💻 IntelliJ IDEA / IDE Setup

You can run, debug, and test the entire project directly within **IntelliJ IDEA** or **PyCharm**:

### 1. Open Project
1. Launch IntelliJ IDEA → **File** → **Open...** → Select the project root folder.
2. In **File** → **Project Structure** (`Ctrl + Alt + Shift + S`) → Set **SDK** to your Python interpreter.
3. In the project tree, right-click `src` → **Mark Directory as** → **Sources Root**.

### 2. Configure One-Click Run Button
1. Click **Run** → **Edit Configurations...** → Click **`+`** → Select **Python**.
2. Configure:
   - **Name**: `Run AWS Support Web App`
   - **Script path**: Select `api\index.py`
   - **Environment variables**: `PORT=8000;PYTHONUNBUFFERED=1`
   - **Working directory**: Project root (`An AI Assistant for Technical Support`)
3. Click **Apply** → **OK**.
4. Click the green **Run ▶️** (or **Debug 🪲**) button in the top toolbar.

---

## 🌐 Vercel Deployment

The repository is structured natively for [Vercel](https://vercel.com/):

```
├── api/
│   └── index.py            # Vercel Serverless Python entrypoint (Flask WSGI)
├── public/                 # Static web client (HTML, CSS, JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── vercel.json             # Vercel routing and build configuration
└── .vercelignore           # Excludes local caches and temporary artifacts
```

### Deploy via Vercel CLI
```bash
npm install -g vercel
vercel
```

### Deploy via GitHub
1. Push your repository to GitHub.
2. Go to your [Vercel Dashboard](https://vercel.com/new) and click **Import Project**.
3. Under **Environment Variables**, set:
   - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
4. Click **Deploy**. Vercel will build the Python serverless backend and static frontend simultaneously.

---

## 🐳 Docker Deployment

To launch the application alongside a containerized MySQL 8.0 instance:

```bash
docker compose up --build -d
```
- Web Application: `http://localhost:8501`
- MySQL Database: `localhost:3306`

To shut down:
```bash
docker compose down
```

---

## 🔑 Default Credentials

For quick evaluation, pre-seeded accounts are ready to use:

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Cloud Engineer** | `demouser` | `DemoUser123!` | Standard User (Personal chat history, queries) |
| **System Administrator** | `admin` | `AdminRoot123!` | Administrator (Audit log inspection, metrics) |

*(You can also create a new account directly via the "Create Account" tab on the login screen).*

---

## 📡 API Endpoints

The Flask REST API serves both frontend interactions and programmatic integrations:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns system health, database connection stats, and model latency. |
| `POST` | `/api/auth/register` | Registers a new user with bcrypt-hashed credentials in MySQL. |
| `POST` | `/api/auth/login` | Authenticates user credentials, sets session token, logs audit event. |
| `POST` | `/api/auth/logout` | Clears active session. |
| `POST` | `/api/chat` | Main query endpoint: classifies intent, retrieves documents, returns solution. |
| `GET` | `/api/chat/history?user_id=<id>` | Fetches previous conversation history for the authenticated user. |
| `DELETE` | `/api/chat/history` | Purges conversation history for the specified user from MySQL. |
| `GET` | `/api/admin/audit-logs` | Admin endpoint retrieving authentication audit trails. |

---

## 🧪 Automated Test Suite

The project includes an automated test suite with **33 passing tests** verifying all layers:

```bash
python -m pytest tests/
```

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1
collected 33 items

tests/test_app.py ...                                                    [  9%]
tests/test_auth.py ......                                                [ 27%]
tests/test_chunking.py ..                                                [ 33%]
tests/test_cleaning.py ...                                               [ 42%]
tests/test_model.py ..........                                           [ 72%]
tests/test_mysql.py ....                                                 [ 84%]
tests/test_rag_pipeline.py ...                                           [ 93%]
tests/test_retrieval.py ..                                               [100%]

======================= 33 passed, 3 warnings in 28.85s =======================
```

---

## 💡 Example Queries to Test

Try entering these queries in the chat bar or clicking the quick chips:

1. **Friendly Interaction (`GREETING`)**:
   > *"Hello! Can you help me with AWS?"*  
   > *Response:* Welcomes the user politely, outlines supported AWS capabilities, and invites questions.

2. **EC2 SSH Permission Denied (`TROUBLESHOOTING`)**:
   > *"How do I fix a Permission denied (publickey) error when connecting to EC2?"*  
   > *Response:* Diagnoses `0644` file permissions, provides `chmod 400 key.pem`, lists default AMI usernames, and shows connection syntax.

3. **S3 NoSuchBucket Error (`TROUBLESHOOTING`)**:
   > *"How do I fix a NoSuchBucket error in Amazon S3?"*  
   > *Response:* Steps to verify case-sensitivity, check regional endpoint `--region`, and list buckets via AWS CLI.

4. **Lambda 3-Second Timeout (`TROUBLESHOOTING`)**:
   > *"How to resolve Task timed out after 3.00 seconds in AWS Lambda?"*  
   > *Response:* Detailed commands to adjust function timeout up to 15 minutes, check VPC NAT Gateways, and optimize execution.

5. **IAM Least Privilege (`SECURITY_BEST_PRACTICE`)**:
   > *"What is the Principle of Least Privilege in AWS IAM?"*  
   > *Response:* Clear explanation with a tightly scoped sample JSON IAM policy granting minimal S3 actions.

6. **Out-of-Scope Rejection (`OUT_OF_SCOPE`)**:
   > *"How do I deploy an application on Azure Virtual Machines?"*  
   > *Response:* Rejects immediately in < 5 ms, politely guiding the user back to AWS Cloud infrastructure.

---

## 🔒 Security & Data Integrity

- **Password Hashing**: Passwords are never stored in plaintext; salted and hashed via `bcrypt` (12 rounds).
- **Audit Logging**: Authentication events (success/failure) are logged with client IP addresses in `audit_logs`.
- **SQL Injection Prevention**: Parameterized queries across all database drivers.
- **Strict Anti-Hallucination**: Queries without supporting knowledge base documentation refuse to fabricate CLI commands.
- **Relational Integrity**: Foreign key constraints with `ON DELETE CASCADE` ensure clean session and history management.

---

<div align="center">
  <sub>Developed for enterprise AWS Cloud technical support automation. Built with Python, Flask, MySQL, ChromaDB, and Vercel.</sub>
</div>
