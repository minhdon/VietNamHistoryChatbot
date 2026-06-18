# Vietnam History Chatbot based on Knowledge Graph (GraphRAG)

This project builds an advanced RAG (Retrieval-Augmented Generation) system tailored for Vietnam History, integrating a **Graph Database (Neo4j)**, **Vector Embeddings**, and **Large Language Models (LLMs)**. The system is capable of extracting historical information, building a Knowledge Graph from raw data, and answering user queries contextually while maintaining conversational memory.

## System Pipeline

![System Pipeline](images/Pipeline.png)

---

## Workflow

The system is divided into two main pipelines: the **Data Ingestion Pipeline** and the **Query & Generation Pipeline**.

### Pipeline 1: Data Processing and Graph Construction
This process transforms raw historical texts/data into a knowledge network and stores it in Neo4j.
* **(1) Preprocessing:** Preprocess the raw dataset for cleaning and standardization.
* **(2) Extract Edges & Nodes:** Extract entities (e.g., historical figures, events, locations) and relationships from the data to form the Graph structure.
* **(3) Generate Embedding:** Pass the graph information through an Embedding Model to convert text/entities into mathematical vectors.
* **(4) Save Embedding:** Store the Nodes, Edges, and Vector Embeddings into the **Neo4j Database**.

### Pipeline 2: Querying and Answer Generation with LLM
The process of handling user questions in real-time.
* **(5) Generate Embedding (User):** The user inputs a query. This query is immediately transformed into a Vector via the Embedding model.
* **(6) Query:** The query is sent to the core backend. It retrieves relevant context from the **Neo4j Database** based on vector similarity and graph relationships.
* **(7) Read Memory:** The application retrieves past chat history from the **Cache Memory** to understand conversational context.
* **(8) Create Prompt:** Synthesize the data to create a complete Prompt: `Base Prompt + User Query + Neo4j Context + Chat History`.
* **(9) Send to LLM:** Send this comprehensive prompt to the **LLM Model** for processing and reasoning.
* **(10) Response:** The LLM returns the generated answer.
* **(11) Save Memory:** The new response is saved back into the **Cache Memory**.
* **(12) Output Answer:** Return the final answer to the User.

---

## Tech Stack

* **Database:** 
  * `Neo4j` (Stores Knowledge Graph & Vector Search)
* **Backend:** Python
* **Frontend:** React TypeScript (Vite)
* **AI / ML:** LLM Models, Embedding Models
* **Infrastructure:** Docker & Docker Compose

---

## Getting Started

### 1. Prerequisites
* Install [Docker](https://docs.docker.com/get-docker/) and Docker Compose.
* Python 3.9+ environment.
* Node.js & npm (for frontend development).

### 2. Environment Setup
Configure your environment variables in the root directory (e.g., `.env`):

```env
# Example Neo4j configurations
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 3. Running the Application

**Using Docker Compose (Recommended)**
```bash
docker-compose up -d
```
This will spin up all necessary services including the Neo4j database, backend, and frontend.

**Running Locally (Development Mode)**

* **Backend:**
  ```bash
  cd backend
  # Ensure you are using a virtual environment
  pip install -r ../requirements.txt
  # Run the backend server
  ```

* **Frontend:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```