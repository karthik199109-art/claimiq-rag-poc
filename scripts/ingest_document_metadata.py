from app.db.database import Base, engine

from app.services.document_ingestion_service import (
    ingest_document_metadata,
)

from app.services.document_reader_service import (
    read_document,
)

from app.services.chunking_service import (
    chunk_document,
)


def main():

    # --------------------------------------------------
    # 1. Create database tables if they don't exist
    # --------------------------------------------------

    Base.metadata.create_all(bind=engine)

    # --------------------------------------------------
    # 2. Existing metadata ingestion
    #    Azure Blob → PostgreSQL
    # --------------------------------------------------

    documents = ingest_document_metadata()

    print(f"Documents processed: {len(documents)}")

    # --------------------------------------------------
    # 3. Read and chunk each document
    # --------------------------------------------------

    for document in documents:

        print(
            f"\nProcessing: {document['document_name']}"
        )

        # ----------------------------------------------
        # Read PDF from Azure Blob
        # ----------------------------------------------

        pages = read_document(
            document["blob_path"]
        )

        print(
            f"Pages extracted: {len(pages)}"
        )

        # ----------------------------------------------
        # Create chunks
        # ----------------------------------------------

        chunks = chunk_document(
            pages=pages,
            document_metadata=document,
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        # ----------------------------------------------
        # Temporary validation
        # Print first 3 chunks only
        # ----------------------------------------------

        for chunk in chunks[:3]:

            print("\n" + "=" * 80)

            print(
                f"Document : {chunk['document_name']}"
            )

            print(
                f"Page     : {chunk['page_number']}"
            )

            print(
                f"Chunk    : {chunk['chunk_number']}"
            )

            print(
                f"Size     : {len(chunk['text'])} characters"
            )

            print("=" * 80)

            print(chunk["text"])


if __name__ == "__main__":
    main()