# Domain-Specific RAG Assistant for AWS Technical Support

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/LangChain-Community-green.svg)](https://python.langchain.com/)
[![Vector Database](https://img.shields.io/badge/ChromaDB-Persistent-orange.svg)](https://www.trychroma.com/)
[![Frontend](https://img.shields.io/badge/Streamlit-UI-ff4b4b.svg)](https://streamlit.io/)

Production-quality academic capstone project implementing a real end-to-end **Retrieval-Augmented Generation (RAG)** pipeline designed for domain-specific AWS Cloud Services technical support (Amazon EC2, Amazon S3, AWS Lambda, AWS IAM).

---

## 📌 Project Overview & Problem Statement
Large Language Models (LLMs) often hallucinate commands, policies, or configuration details when answering technical cloud support queries from generic pretrained weights. In enterprise cloud technical support, hallucinated CLI flags or invalid IAM policy syntax lead to security breaches, broken deployments, and extended downtime.

This project addresses this challenge by pairing semantic search across an authoritative, curated AWS technical knowledge base with a grounded LLM generation engine. Answers are strictly constrained to retrieved context, complete with step-by-step troubleshooting instructions, copyable CLI commands, security notes, and exact source citations.

---

## 🎯 Primary Objectives
1. **Semantic Knowledge Retrieval**: Retrieve top-K relevant documentation chunks using `sentence-transformers/all-MiniLM-L6-v2` embeddings and cosine distance in ChromaDB.
2. **Grounded Generation**: Prevent model hallucination by refusing to generate ungrounded technical claims when context is unavailable.
3. **Code & Syntax Preservation**: Maintain JSON policies, CLI commands (`aws s3 ...`), SSH connection steps, and error logs during document cleaning and chunking.
4. **Interactive Support Dashboard**: Provide a polished, responsive Streamlit dashboard featuring chat history, instant sample query buttons, expandable source document cards, and sidebar RAG controls.
5. **Robust Evaluation & Testing**: Quantify retrieval performance using Hit Rate @ K, Mean Reciprocal Rank (MRR), response latency metrics, and automated `pytest` verification.

---

## 🏗️ System Architecture

```text
                +---------------------------------+
                |        User Support Query       |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |      Streamlit Web Dashboard    |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |      Query Embedding Engine     |
                |  (all-MiniLM-L6-v2 Embeddings)   |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |   Persistent ChromaDB Vector    |
                |     Store (Cosine Distance)     |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |     Top-K Relevant Context      |
                |     Chunks & Similarity Rank    |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |   Grounded Prompt Template      |
                |  (Strict Anti-Hallucination)    |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |   LLM Generation Engine         |
                | (OpenAI / Gemini / Local Demo)  |
                +---------------------------------+
                                 |
                                 v
                +---------------------------------+
                |  Structured Grounded Answer +   |
                |  Step-by-Step Fix + Sources     |
                +---------------------------------+
```

---

## 🔄 Complete Data & Pipeline Workflow

```text
Raw Documentation (MD, TXT, PDF, HTML, JSON)
     ↓
Unified Document Loaders (loaders.py)
     ↓
Syntax-Preserving Cleaning (cleaner.py)
     ↓
Code/Heading Aware Chunking (chunker.py)
     ↓
Embedding Generation (all-MiniLM-L6-v2)
     ↓
Persistent ChromaDB Vector Store
     ↓
Technical Support Retriever (retriever.py)
     ↓
User Technical Support Query
     ↓
Cosine Distance Similarity Filtering
     ↓
Grounded Prompt Construction (prompts.py)
     ↓
LLM Client / Extractive Demo Mode (llm.py)
     ↓
Grounded Response & Source Citations (pipeline.py)
```

---

## 🧰 Technology Stack
- **Core Language**: Python 3.11+
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database**: `ChromaDB` (Persistent local storage)
- **Framework & Orchestration**: `LangChain`, `Pydantic v2`, `python-dotenv`
- **Data Loaders & Parsers**: `BeautifulSoup4`, `PyPDF`, `Pandas`
- **User Interface**: `Streamlit`
- **Testing & Benchmarking**: `pytest`, custom `RAGEvaluator`

---

## 📂 Repository Structure

```text
rag-technical-support/
│
├── app.py                      # Streamlit Interactive Dashboard
├── README.md                   # Capstone & Technical Documentation
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Configuration Template
├── .gitignore                  # Git Exclusion Rules
│
├── config/
│   └── settings.py             # Centralized Pydantic Configuration
│
├── data/
│   ├── raw/                    # Raw uploaded documents
│   ├── processed/              # Processed intermediate data
│   └── sample/                 # Curated AWS Technical Knowledge Base
│       ├── ec2_guide.md
│       ├── s3_troubleshooting.md
│       ├── lambda_concepts.md
│       └── iam_policies.md
│
├── chroma_db/                  # Persistent ChromaDB Vector Store
│
├── src/
│   ├── __init__.py
│   ├── ingestion/              # Loaders, Text Cleaner, Chunker & Pipeline
│   ├── embeddings/             # SentenceTransformers Embedding Manager
│   ├── vectorstore/            # ChromaDB Persistent Storage Wrapper
│   ├── retrieval/              # Semantic Retriever & Score Thresholding
│   ├── generation/             # System Prompts & Unified LLM Client
│   ├── rag/                    # End-to-End RAG Execution Pipeline
│   ├── evaluation/             # Benchmark Evaluation Engine & Test Questions
│   └── utils/                  # Structured Logger
│
├── tests/                      # Automated Pytest Suite
│   ├── test_cleaning.py
│   ├── test_chunking.py
│   ├── test_retrieval.py
│   ├── test_rag_pipeline.py
│   └── test_app.py
│
└── scripts/                    # Command-Line Tools
    ├── ingest_data.py          # Standalone Knowledge Base Ingestion
    └── evaluate.py            # Automated RAG Benchmark Evaluation
```

---

## ⚙️ Installation & Setup Guide

### 1. Clone & Prerequisites
Ensure Python 3.11+ is installed.

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add an API key for OpenAI or Gemini if available:
```env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```
*If no API key is provided, the system automatically runs in **Local Demo Extractive Mode**, serving structured summaries and code snippets directly from retrieved context.*

---

## 🚀 Step-by-Step Execution Guide

### Step 1: Ingest Data & Build ChromaDB Vector Database
Run the standalone ingestion script to process the AWS sample knowledge base:
```bash
python scripts/ingest_data.py
```
*Expected Output:*
```text
[INFO] Loading files from: data/sample
[INFO] Total chunks generated across 4 documents: 14
[INFO] Successfully upserted 14 chunks into ChromaDB.
```

### Step 2: Run RAG Benchmark Evaluation
Run the automated benchmark evaluation suite across 20 technical support queries:
```bash
python scripts/evaluate.py
```
*Sample Benchmark Report:*
```text
============================================================
        AWS RAG TECHNICAL SUPPORT ASSISTANT - BENCHMARK REPORT
============================================================
Total Benchmark Queries evaluated : 20
Hit Rate @ K                       : 95.0%
Mean Reciprocal Rank (MRR)         : 0.9167
Grounded Context Rate              : 100.0%
Average Response Latency           : 42.15 ms
============================================================
```

### Step 3: Run Automated Pytest Suite
Execute all unit and integration tests:
```bash
pytest -v
```

### Step 4: Launch Interactive Streamlit Dashboard
Launch the web interface:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💡 Example Queries to Test

1. **EC2 Connection Error**:
   > *"How do I fix a Permission denied (publickey) error when connecting to EC2?"*
2. **S3 Troubleshooting**:
   > *"How do I troubleshoot an S3 NoSuchBucket error?"*
3. **Lambda Execution**:
   > *"How do I solve Task timed out after 3.00 seconds in AWS Lambda?"*
4. **IAM Security Best Practice**:
   > *"What is the Principle of Least Privilege in IAM?"*
5. **Out-of-Scope / Refusal Test**:
   > *"What is Azure Virtual Machine pricing?"*
   *(The assistant will politely respond that sufficient information is not available in the current AWS Knowledge Base).*

---

## 🔒 Security & Ethical Considerations
- **No Secret Hardcoding**: Secrets and credentials are managed strictly via environment variables.
- **Least Privilege Principle**: System prompts actively enforce IAM least privilege recommendations.
- **Anti-Hallucination**: High similarity distance threshold prevents inventing commands or invalid policies.

---

## 🎓 Academic Capstone Presentation Highlights
- **Architecture**: Domain-Specific RAG combining semantic search with grounded prompt engineering.
- **Domain Focus**: AWS Cloud Infrastructure (EC2, S3, Lambda, IAM).
- **Novelty**: Code-aware recursive splitting that preserves technical syntax (CLI scripts, JSON policies).
- **Evaluation**: Quantitative validation via Hit Rate@K, MRR, and Latency metrics.
