**Vietnam History Chatbot based on Knowledge Graph (GraphRAG)** \hfill 09/2025 – 01/2026  
*Team size: 1 | GitHub: [github.com/minhdon/Vietnam_History_Chatbot](https://github.com/minhdon/Vietnam_History_Chatbot)*  
- Designed and implemented a GraphRAG system integrating a Neo4j Graph Database, Vector Embeddings, and Large Language Models (LLMs), achieving a **improvement in factual accuracy** compared to standard RAG baselines when answering complex Vietnam history queries.
- Built a Data Ingestion Pipeline that processed over **1,000,000 raw historical text chunks**, extracting **20,000+ distinct entities** and **50,000+ relationships** to construct a comprehensive Knowledge Graph in Neo4j.
- Developed a real-time Query & Generation Pipeline that retrieves context via vector similarity and graph traversal, utilizing Redis-based cache memory to synthesize prompts and reducing average response latency to **under 1.2 seconds**.
- Orchestrated the full-stack architecture using Python (Backend), React TypeScript (Frontend), and Docker Compose, seamlessly deploying **4 containerized microservices** (Frontend, Backend, Neo4j, Cache).
- **Tools:** Python, React TypeScript, Neo4j, LLMs, Vector Embeddings, Docker.
