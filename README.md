# 🛍️ Shoply — E-commerce RAG Support Assistant

Shoply is an AI-powered customer support assistant for an e-commerce store. It uses **Retrieval-Augmented Generation (RAG)** to answer customer questions based on the store's actual policy documents.

Instead of relying only on the language model's general knowledge, Shoply retrieves relevant information from the store's policy documents and provides that information to the AI model to generate the final answer.

🔗 **Live Demo:** https://shoply-ly6s.onrender.com/

🔗 **GitHub Repository:** https://github.com/dilliram-code/shoply

---

## 📌 Project Overview

Customer support systems often need to answer questions such as:

* What is the return policy?
* How long does shipping take?
* Can I get a refund?
* What is covered by the warranty?
* How can I return a product?
* How long do I have to request a refund?

Shoply provides an AI chatbot that can answer these questions using information stored in the company's policy documents.

The project demonstrates the basic architecture of a **Retrieval-Augmented Generation (RAG)** application using:

* PDF documents as the knowledge source
* OpenAI embeddings
* Pinecone vector database
* OpenAI language model
* FastAPI backend
* HTML/CSS/JavaScript frontend

---

## 🧠 How RAG Works in Shoply

The system follows this general pipeline:

```text
                ┌─────────────────────┐
                │   Customer Question │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Generate Embedding  │
                │   OpenAI Embedding  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Search Pinecone    │
                │   Vector Database   │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Relevant Policy     │
                │     Chunks          │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │      OpenAI LLM     │
                │ Context + Question  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     Final Answer    │
                └─────────────────────┘
```

### Example

Suppose a customer asks:

> "Can I return a product after 20 days?"

Shoply does not simply ask the LLM to answer from its general knowledge.

Instead:

1. The question is converted into an embedding.
2. Pinecone searches for semantically similar policy information.
3. Relevant sections from the return-policy document are retrieved.
4. The retrieved information is provided to the LLM as context.
5. The LLM generates the final response using the retrieved company information.

This helps keep the answer grounded in the store's actual policies.

---

## 📚 Knowledge Base

The current knowledge base contains policy documents related to the store:

```text
knowledge/
│
├── return-policy.pdf
├── shipping-policy.pdf
├── refund-policy.pdf
└── warranty-policy.pdf
```

These documents are converted into smaller text chunks before being embedded and stored in Pinecone.

---

## 🏗️ Project Structure

```text
shoply/
│
├── knowledge/
│   ├── return-policy.pdf
│   ├── shipping-policy.pdf
│   ├── refund-policy.pdf
│   └── warranty-policy.pdf
│
├── static/
│   ├── index.html
│
├── main.py
├── server.py
├── requirements.txt
├── .gitignore
└── README.md
```

### `main.py`

Contains the core RAG logic:

* Loading PDF documents
* Splitting documents into chunks
* Creating embeddings
* Uploading vectors to Pinecone
* Performing similarity search
* Sending retrieved context to the LLM
* Generating the final answer

### `server.py`

Contains the FastAPI application.

It provides API endpoints for:

* Health checking
* Chat requests
* Knowledge-base ingestion
* Serving the frontend

### `knowledge/`

Contains the PDF documents used as the knowledge base.

### `static/`

Contains the frontend interface for interacting with the chatbot.

---

## ⚙️ Technologies Used

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Main programming language |
| FastAPI    | Backend API               |
| OpenAI     | Embeddings and LLM        |
| Pinecone   | Vector database           |
| PyPDF      | Reading PDF documents     |
| tiktoken   | Token-based text chunking |
| HTML       | Frontend structure        |
| CSS        | Frontend styling          |
| JavaScript | Frontend interaction      |
| Render     | Deployment                |

---

## 🔑 Environment Variables

The project requires API keys for OpenAI and Pinecone.

Create a `.env` file locally:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=shop-support
PINECONE_NAMESPACE=policies
```

### Environment variable explanation

#### `OPENAI_API_KEY`

Your OpenAI API key used for:

* Generating embeddings
* Generating chatbot responses

#### `PINECONE_API_KEY`

Your Pinecone API key used to access the vector database.

#### `PINECONE_INDEX_NAME`

The name of the Pinecone index.

For this project:

```env
PINECONE_INDEX_NAME=shop-support
```

This is **not an API key**.

#### `PINECONE_NAMESPACE`

The namespace used to store the policy vectors:

```env
PINECONE_NAMESPACE=policies
```

---

## 🚀 Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/dilliram-code/shoply.git
```

Move into the project:

```bash
cd shoply
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=shop-support
PINECONE_NAMESPACE=policies
```

Do not commit `.env` to GitHub.

---

### 5. Start the FastAPI server

Run:

```bash
python -m uvicorn server:app --reload
```

The application should be available at:

```text
http://127.0.0.1:8000
```

---

## 📥 Loading the Knowledge Base

Before asking questions, the PDF documents need to be processed and uploaded to Pinecone.

The project provides an ingestion endpoint:

```http
POST /api/ingest
```

For example:

```bash
curl -X POST http://127.0.0.1:8000/api/ingest
```

This will:

1. Read the PDF files.
2. Extract their text.
3. Split the text into chunks.
4. Generate embeddings.
5. Store the vectors in Pinecone.

The ingestion process should be run when the knowledge documents are added or changed.

---

## 💬 Chat API

The chatbot provides the following endpoint:

```http
POST /api/chat
```

Example request:

```json
{
  "question": "What is your return policy?"
}
```

Example response:

```json
{
  "answer": "..."
}
```

---

## ❤️ Health Check

The application also provides a health-check endpoint:

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok"
}
```

---

## 🔍 RAG Pipeline in Detail

### 1. PDF Loading

The application reads the policy PDFs from the `knowledge/` directory.

```text
PDF
 ↓
Text Extraction
```

---

### 2. Text Chunking

Large documents are divided into smaller token-based chunks.

```text
Large PDF
   ↓
Extracted Text
   ↓
Text Chunks
   ↓
Chunk 1
Chunk 2
Chunk 3
...
```

This makes semantic retrieval more effective.

---

### 3. Embedding Generation

Each chunk is converted into a numerical vector using:

```text
text-embedding-3-small
```

The vectors represent the semantic meaning of the text.

```text
Policy Text
     ↓
OpenAI Embedding Model
     ↓
Vector Representation
```

---

### 4. Vector Storage

The embeddings are stored in Pinecone.

```text
Document Chunk
      ↓
Embedding
      ↓
Pinecone
```

Each stored vector also contains metadata such as the original document and chunk information.

---

### 5. Query Embedding

When a customer asks a question, the question is also converted into an embedding.

```text
Customer Question
        ↓
Embedding Model
        ↓
Query Vector
```

---

### 6. Similarity Search

The query vector is sent to Pinecone.

Pinecone searches for the most semantically similar policy chunks.

```text
Query Vector
     ↓
Pinecone
     ↓
Top Relevant Chunks
```

---

### 7. Context Construction

The retrieved chunks are combined into a context that is sent to the language model.

```text
Retrieved Chunk 1
Retrieved Chunk 2
Retrieved Chunk 3
Retrieved Chunk 4
        ↓
     Context
```

---

### 8. Answer Generation

The LLM receives:

```text
System Instructions
        +
Retrieved Company Information
        +
Customer Question
```

and generates the final response.

The assistant is instructed to use the company information rather than inventing policy information.

---

## 🛡️ Hallucination Control

One of the important concepts demonstrated by this project is **grounding an LLM using external knowledge**.

The assistant is instructed to answer using the retrieved company information.

If the required information is not available, it can respond:

```text
I don't have that information in the company documents.
```

This is preferable to allowing the model to invent a company policy.

However, RAG does not completely eliminate hallucinations. Production systems should also consider:

* Better retrieval strategies
* Reranking
* Metadata filtering
* Citation/source display
* Evaluation datasets
* Retrieval quality monitoring
* Guardrails
* Human escalation

---

## 🌐 Deployment

The application is deployed using **Render**.

### Live Application

👉 https://shoply-ly6s.onrender.com/

The backend runs using:

```bash
python -m uvicorn server:app --host 0.0.0.0 --port $PORT
```

Environment variables are configured through the Render dashboard rather than committing API keys to the repository.

---

## 🧪 Example Questions

You can try questions such as:

```text
What is the return policy?

How many days do I have to return a product?

How long does shipping take?

Can I get a refund?

What products are covered by the warranty?

How can I request a return?

What happens if my product arrives damaged?
```

You can also ask questions that are unrelated to the available documents and observe how the system handles information that is not present in its knowledge base.

---

## 🎯 Learning Objectives

This project was built to understand the fundamental concepts behind modern RAG applications.

Through this project, the following concepts are demonstrated:

* Large Language Models
* Embeddings
* Vector databases
* Semantic search
* Document chunking
* PDF processing
* Retrieval-Augmented Generation
* Prompt grounding
* FastAPI
* REST APIs
* Environment variables
* Backend/frontend integration
* Cloud deployment

---

## 🔮 Possible Future Improvements

The current project demonstrates a basic RAG architecture. It can be extended into a more production-oriented customer support system.

Possible improvements include:

### 1. Conversation Memory

Store previous user and assistant messages so that the chatbot can understand follow-up questions.

### 2. Source Citations

Show the customer which policy document was used to generate the answer.

Example:

```text
Source: return-policy.pdf
```

### 3. Better Retrieval

Introduce:

* Hybrid search
* Sparse + dense retrieval
* Reranking
* Metadata filtering

### 4. Document Management

Add an admin interface for uploading and updating policy documents without modifying the source code.

### 5. Customer Authentication

Connect the assistant with a customer account system.

This could allow questions such as:

```text
Where is my order?

Can I cancel my order?

What is the status of my refund?
```

### 6. Database Integration

Connect the chatbot to an actual e-commerce database containing:

* Customers
* Orders
* Products
* Payments
* Returns
* Refunds

### 7. Agentic Workflows

The RAG chatbot could eventually become an AI agent capable of deciding when to:

```text
Search policies
      ↓
Check order database
      ↓
Check refund status
      ↓
Create support ticket
      ↓
Respond to customer
```

This would move the system beyond a simple RAG chatbot toward an **agentic customer-support system**.

---

## ⚠️ Disclaimer

This project is primarily a learning and demonstration project.

The current implementation is not intended to be used as a complete production e-commerce customer-support platform without additional security, monitoring, authentication, evaluation, error handling, and infrastructure improvements.

API keys and other secrets should always be stored securely using environment variables or a dedicated secret-management system.

---

## 👨‍💻 Author

**Dilli Ram Chaudhary**

B.Sc. Physics | AI/ML Student | Python & AI Enthusiast

GitHub:
https://github.com/dilliram-code

---

## ⭐ Project

If you find this project useful for learning RAG, feel free to explore the repository and experiment with the implementation.

**Live Demo:**
https://shoply-ly6s.onrender.com/

**Source Code:**
https://github.com/dilliram-code/shoply
