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
