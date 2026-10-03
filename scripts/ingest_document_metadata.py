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

from app.services.embedding_service import (
    generate_embeddings,
)


def main():

    # --------------------------------------------------
    # 1. Create database tables
    # --------------------------------------------------

    Base.metadata.create_all(
        bind=engine
    )

    # --------------------------------------------------
    # 2. Discover documents
    # --------------------------------------------------

    documents = ingest_document_metadata()

    print(
        f"\nDocuments processed: "
        f"{len(documents)}"
    )

    # --------------------------------------------------
    # 3. Process each document
    # --------------------------------------------------

    for document in documents:

        print("\n" + "=" * 80)

        print(
            f"Processing: "
            f"{document['document_name']}"
        )

        print("=" * 80)

        # --------------------------------------------------
        # Read PDF
        # --------------------------------------------------

        pages = read_document(
            document["blob_path"]
        )

        print(
            f"Pages extracted: "
            f"{len(pages)}"
        )

        # --------------------------------------------------
        # Chunk PDF
        # --------------------------------------------------

        chunks = chunk_document(
            pages=pages,
            document_metadata=document,
        )

        print(
            f"Chunks created: "
            f"{len(chunks)}"
        )

        # --------------------------------------------------
        # Generate embeddings
        # --------------------------------------------------

        chunks = generate_embeddings(
            chunks
        )

        print(
            f"Embeddings created: "
            f"{len(chunks)}"
        )

        # --------------------------------------------------
        # Verify first chunk
        # --------------------------------------------------

        if chunks:

            first_chunk = chunks[0]

            print("\nFirst chunk verification:")

            print(
                f"Document: "
                f"{first_chunk['document_name']}"
            )

            print(
                f"Page: "
                f"{first_chunk['page_number']}"
            )

            print(
                f"Chunk: "
                f"{first_chunk['chunk_number']}"
            )

            print(
                f"Text size: "
                f"{len(first_chunk['text'])} characters"
            )

            print(
                f"Embedding dimensions: "
                f"{len(first_chunk['embedding'])}"
            )

            print(
                f"First 5 embedding values: "
                f"{first_chunk['embedding'][:5]}"
            )


if __name__ == "__main__":
    main()