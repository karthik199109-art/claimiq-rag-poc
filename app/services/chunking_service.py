CHUNK_SIZE = 1800
CHUNK_OVERLAP = 200


def chunk_text(text: str, page_number: int, document_metadata: dict):
    """
    Split text into chunks of CHUNK_SIZE characters
    with CHUNK_OVERLAP characters of overlap.
    """

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + CHUNK_SIZE

        chunk = {
            "document_id": document_metadata["document_id"],
            "document_name": document_metadata["document_name"],
            "document_type": document_metadata["document_type"],
            "document_group_id": document_metadata["document_group_id"],
            "version": document_metadata["version"],
            "blob_path": document_metadata["blob_path"],
            "page_number": page_number,
            "text": text[start:end],
        }

        chunks.append(chunk)

        if end >= text_length:
            break

        start = end - CHUNK_OVERLAP

    return chunks


def chunk_document(pages, document_metadata):
    """
    Chunk all pages of a document.
    """

    all_chunks = []
    chunk_number = 1

    for page in pages:

        page_chunks = chunk_text(
            text=page["text"],
            page_number=page["page_number"],
            document_metadata=document_metadata,
        )

        for chunk in page_chunks:

            chunk["chunk_number"] = chunk_number

            all_chunks.append(chunk)

            chunk_number += 1

    return all_chunks