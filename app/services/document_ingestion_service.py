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

    for blob in container_client.list_blobs():

        blob_name = blob.name

        # Ignore anything that is not a PDF
        if not blob_name.lower().endswith(".pdf"):
            continue

        # Folder/category
        path_parts = blob_name.split("/")

        if len(path_parts) > 1:
            category = path_parts[0]
        else:
            category = "unknown"

        document_name = os.path.basename(blob_name)

        document_id = str(uuid.uuid4())
       

        now = datetime.now(timezone.utc)

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

        insert_document(document_data)

        print(
            f"Inserted: {document_name} "
            f"| Category: {category} "
            f"| Blob path: {blob_name}"
        )