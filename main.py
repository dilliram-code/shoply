import hashlib                # to create unique id to every chunk
import os                     # to read env variable
import sys 
from pathlib import Path
import tiktoken
from openai import OpenAI 
from pinecone import Pinecone
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

api_key =os.getenv("OPENAI_API_KEY")

PDF_DIR = Path("knowledge")

# pinecone index
INDEX_NAME = os.getenv(
  "PINECONE_INDEX_NAME",
  "shop-support"
  )

NAMESPACE = os.getenv(
  "PINECONE_NAMESPACE",
  "policies"
)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1024
CHAT_MODEL = "gpt-5-mini"
CHUNK_SIZE = 300
TOP_K = 4

# get the api keys
def require_key(name: str) -> str:
  value = os.getenv(name)
  
  if not value: 
    raise RuntimeError(f"Set {name} before running the program.")
  
  return value

openai_client = OpenAI(api_key=require_key(api_key))
pinecone_client = Pinecone(api_key=require_key("PINECONE_API_KEY"))
pinecone_index = pinecone_client.Index(INDEX_NAME)
tokenizer = tiktoken.get_encoding("cl100k_base")

# split into token chunks
def split_into_token_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    tokens = tokenizer.encode(text)
    chunks = []

    for start in range(0, len(tokens), chunk_size):
        chunk = tokenizer.decode(tokens[start : start + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)

    return chunks

# read the pdfs
def read_knowledge_base() -> list[dict]:
    chunks = []

    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        for chunk_number, chunk_text in enumerate(split_into_token_chunks(text)):
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": pdf_path.name,
                        "chunk": chunk_number,
                    },
                }
            )

    return chunks
  
# create unique ids
def stable_id(chunk: dict) -> str:
    raw_id = (
        f"{chunk['metadata']['source']}:{chunk['metadata']['chunk']}:{chunk['text']}"
    )
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

# rag ingestion
def load_knowledge_base() -> int:
    chunks = read_knowledge_base()
    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embedding_response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[chunk["text"] for chunk in batch],
            dimensions=EMBEDDING_DIMENSIONS,
        )

        # create pinecone records
        records = []
        for chunk, embedding in zip(batch, embedding_response.data):
            records.append(
                {
                    "id": stable_id(chunk),
                    "values": embedding.embedding,
                    "metadata": {**chunk["metadata"], "text": chunk["text"]},
                }
            )

        # insert if new or upload if already exists
        pinecone_index.upsert(vectors=records, namespace=NAMESPACE)

    return len(chunks)

# embed the user question into vector embedding
def answer_user_query(question: str) -> str:

    # embed the question
    query_embedding = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=question,
        dimensions=EMBEDDING_DIMENSIONS,
    )

    # search the most relevant 4 vectors in vector database
    search_result = pinecone_index.query(
        vector=query_embedding.data[0].embedding,
        top_k=TOP_K,
        include_metadata=True,
        namespace=NAMESPACE,
    )

    # extract the retrieved text
    context = "\n\n".join(
        match.metadata.get("text", "")
        for match in search_result.matches
        if match.metadata and match.metadata.get("text")
    )

    instructions = f'''You are an AI customer support assistant for our e-commerce company.

    Answer the customer using ONLY the company information provided below.

    If the answer is not available in the provided information, say:
    "I don't have that information in the company documents."

    COMPANY INFORMATION
    {context}'''

    # gpt generates the actual answer
    response = openai_client.responses.create(
        model=CHAT_MODEL,
        instructions=instructions,
        input=question,
    )
    return response.output_text

def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the return policy?"
    chunk_count = load_knowledge_base()
    print(f"Loaded {chunk_count} knowledge chunks.")

    # Simple function call; no REST API or web framework is used.
    answer = answer_user_query(question)
    print(answer)


if __name__ == "__main__":
    main()