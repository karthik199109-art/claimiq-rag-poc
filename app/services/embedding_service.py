from openai import AzureOpenAI

from app.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BATCH_SIZE = 100


# --------------------------------------------------
# Azure OpenAI Client
# --------------------------------------------------

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-10-21",
)


# --------------------------------------------------
# Generate embeddings in batches
# --------------------------------------------------

def generate_embeddings(chunks):

    total_chunks = len(chunks)

    print(
        f"\nTotal chunks to embed: {total_chunks}"
    )

    print(
        f"Batch size: {BATCH_SIZE}"
    )

    for start in range(
        0,
        total_chunks,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total_chunks
        )

        batch = chunks[start:end]

        print(
            f"\nEmbedding batch "
            f"{start + 1}-{end} "
            f"of {total_chunks}"
        )

        # Extract only the text
        texts = [
            chunk["text"]
            for chunk in batch
        ]

        # Send entire batch in one API request
        response = client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            input=texts,
        )

        # Attach embeddings back to chunks
        for chunk, embedding_data in zip(
            batch,
            response.data
        ):

            chunk["embedding"] = (
                embedding_data.embedding
            )

        print(
            f"Completed batch "
            f"{start + 1}-{end}"
        )

    return chunks