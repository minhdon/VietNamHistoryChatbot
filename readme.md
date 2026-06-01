# News Analysis & Text Generation System Architecture based on Knowledge Graph (GraphRAG)

This project builds an advanced RAG (Retrieval-Augmented Generation) system, integrating a **Graph Database (Neo4j)**, **Vector Embeddings**, and **Large Language Models (LLMs)**. The system is capable of extracting information, building a Knowledge Graph from raw data, and answering user queries contextually while maintaining conversational memory (Memory Cache).

## System Pipeline

![System Pipeline](images/Pipeline.png)

---

## Workflow

The system is divided into two main pipelines: the **Data Ingestion Pipeline** and the **Query & Generation Pipeline**.

### Pipeline 1: Data Processing and Graph Construction (Top Pipeline)
This process transforms raw tabular/text data into a knowledge network and stores it in Neo4j.
* **(1) Preprocessing:** Preprocess the raw dataset for cleaning and standardization.
* **(2) Extract Edges & Nodes:** Extract entities (Nodes) and relationships (Edges) from the data to form the Graph structure.
* **(3) Generate Embedding:** Pass the graph information through an Embedding Model to convert text/entities into mathematical vectors.
* **(4) Save Embedding:** Store the Nodes, Edges, and Vector Embeddings into the **Neo4j Database**.

### Pipeline 2: Querying and Answer Generation with LLM (Bottom Pipeline)
The process of handling user questions in real-time.
* **(5) Generate Embedding (User):** The user inputs a query. This query is immediately transformed into a Vector via the Embedding model.
* **(6) Query:** The query is sent to the core application (GenAI App). This app retrieves relevant context from the **Neo4j Database** based on vector similarity and graph relationships.
* **(7) Read Memory:** The GenAI App retrieves past chat history from the **Cache Memory** (e.g., Redis or In-memory) to understand the conversational context.
* **(8) Create Prompt:** Synthesize the data to create a complete Prompt, including: `Base Prompt + User Query + Neo4j Context + Chat History`.
* **(9) Send to LLM:** Send this comprehensive prompt to the **LLM Model** for processing and reasoning.
* **(10) Response:** The LLM returns the generated answer to the GenAI App.
* **(11) Save Memory:** The new response is saved back into the **Cache Memory** to serve subsequent user queries.
* **(12) Output Answer:** Return the final answer to the User.

---

## Tech Stack

* **Database:** * `Neo4j` (Stores Knowledge Graph & Vector Search)
  * `PostgreSQL` (Stores Metadata & structured data)
* **Backend:** Python 
* **Frontend:** React TSX
* **AI / ML:** LLM Models, Embedding Models.
* **Infrastructure:** Docker & Docker Compose for container management.

---

## Getting Started

### 1. Prerequisites
* Install [Docker](https://docs.docker.com/get-docker/) and Docker Compose.
* Python 3.9+ environment (if running code locally).

### 2. Environment Setup
Create a `.env` file in the root directory containing the security configurations based on the `.env.example` file:

```env
# Example .env file content
DB_USER=minh_admin
DB_PASSWORD=your_secret_password
DB_NAME=news_intelligence
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=your_secret_password