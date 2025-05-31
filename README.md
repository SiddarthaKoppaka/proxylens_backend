# ProxyLens Backend

ProxyLens is a powerful RAG-based document retrieval and generation system designed for long HTML documents with deep contextual metadata. The backend orchestrates multiple components, including vector stores, metadata search, and LLM-driven tools to provide highly relevant and explainable summaries for complex documents.

---

## 🧠 Core Features

* 🔍 **Semantic Search using Qdrant + Metadata Filtering**
* 🏷️ **Auto Metadata Tagging using LLaMA-3 model**
* 🗃️ **Self Querying Retriever** (LangChain) for context-aware search
* 🌐 **Tavily Web Search fallback**
* 📈 **LLM Evaluation Layer** to assess retrieval quality
* 🧭 **Intelligent Router** to choose between retriever/metadata/web
* 📦 **Multi-source Retrieval Pipeline**: Vector DB, CSV, Web
* 🛠️ **Modular Microservices with FastAPI**

---

## 🏗️ Backend Architecture

![RAG - Proxy](https://github.com/user-attachments/assets/711f7ffc-ae8f-4e36-9177-14d18e29c375)

---

## 📦 Ingestion Pipeline

* Long HTML files are parsed, chunked, and passed through a LLaMA-3 model.
* Metadata such as date, category, source, and LLM-generated tags are appended.
* Embedded using Sentence Transformers (`all-mpnet-base-v2`).
* Data stored in AWS EC2-hosted **Qdrant Vector Store** with EBS volume for persistence.

---

## 🚀 Deployment Architecture

### ⚙️ Tech Stack:

* **Backend API**: FastAPI (Python)
* **LLMs**: Ollama (LLaMA-3 based), locally hosted
* **Retriever**: LangChain SelfQueryRetriever
* **Vector DB**: Qdrant (hosted on EC2 with persistent EBS)
* **Metadata**: CSV-based fallback, optionally enhanced with Tavily Web Search
* **Orchestration**: Kubernetes via Minikube (for dev)

### 📁 Kubernetes Deployment Includes:

* `rag-backend`: FastAPI server (with LLM calls, router, retriever, generator)
* `ollama-service`: Lightweight container with LLaMA-3 model preloaded
* `qdrant`: Already hosted on AWS (external URL)

---

### ✅ Deployment Steps (Locally with Minikube):

1. **Connect to Minikube Docker Daemon**:

```bash
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

2. **Build Images**:

```bash
cd proxylens_backend
docker build -t rag-backend-slim .

cd ../ollama_docker
docker build -t ollama-llama3 .
```

3. **Apply Kubernetes Configurations**:

```bash
kubectl apply -f k8s-deployment.yaml
```

4. **Check Services**:

```bash
kubectl get all -n proxylens-ai
```

5. **Test Connectivity**:

```bash
kubectl exec -it deploy/rag-backend -n proxylens-ai -- sh
python
>>> import requests
>>> requests.post("http://ollama-service:11434/api/generate", json={...})
```

---

## 🧪 Testing & Evaluation

* Every query is routed and evaluated using a local `Evaluation LLM`.
* Outputs compared for relevance, precision, coverage.
* Logs tracked via logging module inside `utils/`.

---

## 📁 Code Structure

```
proxylens_backend/
├── Dockerfile
├── requirements.txt
└── src/
    ├── main.py               # Entry Point
    ├── agents/               # RAG Agents
    ├── api/v1/               # FastAPI Routes
    ├── core/                 # Config & Security
    ├── db/                   # Chat Memory & Metadata
    ├── models/               # Placeholder for future use
    ├── services/             # Generator, Retriever, Web Search
    └── utils/                # Logging, Utilities
```

---

## 📫 Contact

For access or demo requests, reach out to the maintainer privately.

> This backend is strictly for academic and internal demo purposes. The documents used are not disclosed.

---
