import os
from io import BytesIO

import chromadb
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from openai import AzureOpenAI
from pypdf import PdfReader


# --------------------------------
# Load environment variables
# --------------------------------

load_dotenv()

storage_connection_string = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

container_name = os.getenv(
    "AZURE_STORAGE_CONTAINER"
)

azure_openai_endpoint = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)

azure_openai_api_key = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

embedding_deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)


# --------------------------------
# Connect to Azure Blob Storage
# --------------------------------

blob_service_client = BlobServiceClient.from_connection_string(
    storage_connection_string
)

container_client = blob_service_client.get_container_client(
    container_name
)


# --------------------------------
# Connect to Azure OpenAI
# --------------------------------

openai_client = AzureOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version="2024-10-21",
)


# --------------------------------
# Connect to ChromaDB
# --------------------------------

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="policy_documents"
)


# --------------------------------
# Chunking function
# --------------------------------

def chunk_text(text, chunk_size=1000, overlap=200):

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


# --------------------------------
# Store all chunks and embeddings
# --------------------------------

all_chunks = []
all_embeddings = []


# --------------------------------
# Process all PDFs
# --------------------------------

for blob in container_client.list_blobs():

    if not blob.name.lower().endswith(".pdf"):
        continue

    print("\n--------------------------------")
    print(f"Processing: {blob.name}")
    print("--------------------------------")

    # Download PDF
    blob_client = container_client.get_blob_client(
        blob.name
    )

    pdf_data = blob_client.download_blob().readall()

    # Read PDF
    reader = PdfReader(
        BytesIO(pdf_data)
    )

    # --------------------------------
    # Extract text page by page
    # --------------------------------

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        page_text = page.extract_text()

        if not page_text:
            continue

        print(
            f"Processing page {page_number}"
        )

        # --------------------------------
        # Create chunks for this page
        # --------------------------------

        chunks = chunk_text(page_text)

        print(
            f"Page {page_number} → "
            f"{len(chunks)} chunks"
        )

        # --------------------------------
        # Create embeddings
        # --------------------------------

        for index, chunk in enumerate(chunks):

            response = openai_client.embeddings.create(
                model=embedding_deployment,
                input=chunk,
            )

            embedding = response.data[0].embedding

            # --------------------------------
            # Store chunk information
            # --------------------------------

            all_chunks.append(
                {
                    "id": (
                        f"{blob.name}"
                        f"_page_{page_number}"
                        f"_chunk_{index}"
                    ),

                    "text": chunk,

                    "source": blob.name,

                    "page": page_number,
                }
            )

            # --------------------------------
            # Store embedding
            # --------------------------------

            all_embeddings.append(
                embedding
            )

            print(
                f"Embedded page "
                f"{page_number}, "
                f"chunk {index + 1}/"
                f"{len(chunks)}"
            )


# --------------------------------
# Store data in ChromaDB
# --------------------------------

print("\n================================")
print("Storing data in ChromaDB")
print("================================")


for i, chunk in enumerate(all_chunks):

    collection.add(

        ids=[
            chunk["id"]
        ],

        documents=[
            chunk["text"]
        ],

        embeddings=[
            all_embeddings[i]
        ],

        metadatas=[
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "status": "active",
            }
        ]
    )


# --------------------------------
# Verification
# --------------------------------

print("\n================================")
print("PROCESSING COMPLETED")
print("================================")

print(
    f"Total chunks: {len(all_chunks)}"
)

print(
    f"Total embeddings: {len(all_embeddings)}"
)

print(
    f"Documents stored in ChromaDB: "
    f"{collection.count()}"
)


# --------------------------------
# Show documents processed
# --------------------------------

print("\nDocuments processed:")

documents = set(
    chunk["source"]
    for chunk in all_chunks
)

for document in documents:

    document_chunks = [
        chunk
        for chunk in all_chunks
        if chunk["source"] == document
    ]

    print(
        f"{document} → "
        f"{len(document_chunks)} chunks"
    )