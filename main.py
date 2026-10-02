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

