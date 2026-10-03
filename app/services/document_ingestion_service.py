import os
import uuid

from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient

from app.config.settings import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_STORAGE_CONTAINER,
)

from app.repositories.document_repository import insert_document


def ingest_document_metadata():

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )

    container_client = blob_service_client.get_container_client(
        AZURE_STORAGE_CONTAINER
    )

    # Store all successfully inserted documents
    inserted_documents = []

    for blob in container_client.list_blobs():

        blob_name = blob.name

        # Ignore anything that is not a PDF
        if not blob_name.lower().endswith(".pdf"):
            continue

        # Get folder/category from blob path
        path_parts = blob_name.split("/")

        if len(path_parts) > 1:
            category = path_parts[0]
        else:
            category = "unknown"

        # Get only the file name
        document_name = os.path.basename(blob_name)

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        # Current UTC timestamp
        now = datetime.now(timezone.utc)

        # Document metadata
        document_data = {
            "document_id": document_id,
            "document_name": document_name,
            "document_type": "POLICY",
            "document_group_id": document_id,
            "version": 1,
            "status": "PROCESSING",
            "blob_path": blob_name,
            "uploaded_by": "system",
            "uploaded_at": now,
            "activated_at": None,
            "deactivated_at": None,
        }

        # Insert metadata into PostgreSQL
        insert_document(document_data)

        # Keep the inserted document metadata
        # so the next stage can read and process it
        inserted_documents.append(document_data)

        print(
            f"Inserted: {document_name} "
            f"| Category: {category} "
            f"| Blob path: {blob_name}"
        )

    return inserted_documents