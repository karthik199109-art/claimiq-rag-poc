from io import BytesIO

from azure.storage.blob import BlobServiceClient
from pypdf import PdfReader

from app.config.settings import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_STORAGE_CONTAINER,
)


def read_document(blob_path: str):
    """
    Download a PDF from Azure Blob Storage
    and extract text page by page.
    """

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER,
        blob=blob_path,
    )

    # Download PDF
    pdf_bytes = blob_client.download_blob().readall()

    # Read PDF
    reader = PdfReader(BytesIO(pdf_bytes))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages