import hashlib                # to create unique id to every chunk
import os                     # to read env variable
import sys 
from pathlib import Path
import tiktoken
from openai import OpenAI 
from pinecone import Pinecone
from pypdf import PdfReader

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

openai_client = OpenAI(api_key=require_key("OPENAI_API_KEY"))
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