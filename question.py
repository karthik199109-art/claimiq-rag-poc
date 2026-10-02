import os
import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# ============================================
# Environment variables
# ============================================

azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

embedding_deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)

chat_deployment = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT"
)

# ============================================
# Azure OpenAI client - Embeddings
# ============================================

embedding_client = AzureOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version="2024-10-21",
)

# ============================================
# Azure OpenAI client - LLM / Responses API
# ============================================

llm_client = AzureOpenAI(
    api_key=azure_openai_api_key,
    azure_endpoint=azure_openai_endpoint,
    api_version="2025-03-01-preview",
)

# ============================================
# ChromaDB
# ============================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="policy_documents"
)

print(
    "Documents stored in ChromaDB:",
    collection.count()
)

# ============================================
# Ask a question
# ============================================

question = input("\nAsk your question: ")

print("\nYour question:", question)

# ============================================
# Create embedding for question
# ============================================

response = embedding_client.embeddings.create(
    model=embedding_deployment,
    input=question
)

question_embedding = response.data[0].embedding

print("\nQuestion embedding created.")
print(
    "Embedding dimensions:",
    len(question_embedding)
)

# ============================================
# Search ChromaDB
# ============================================

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=3
)

# ============================================
# Get Top-K results
# ============================================

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

MAX_DISTANCE = 0.75

relevant_results = []

for i in range(len(documents)):

    if distances[i] <= MAX_DISTANCE:

        relevant_results.append(
            {
                "text": documents[i],
                "source": metadatas[i]["source"],
                "distance": distances[i]
            }
        )

# ============================================
# Display retrieved chunks
# ============================================

if not relevant_results:

    print(
        "\nNo relevant information found "
        "in the approved documents."
    )

else:

    print("\nRelevant chunks:\n")

    for result in relevant_results:

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Distance: {result['distance']}"
        )

        print(
            result["text"]
        )

        print("\n--------------------")

# ============================================
# Build context
# ============================================

context = ""

for result in relevant_results:

    context += (
        f"Source: {result['source']}\n"
        f"{result['text']}\n\n"
    )

print("\nContext for LLM:")
print(context)

# ============================================
# Build prompt
# ============================================

prompt = f"""
You are an insurance policy assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context,
say: "No relevant information found in the approved documents."

Do not use outside knowledge.
Do not make up policy clauses.

Context:
{context}

Question:
{question}
"""

# ============================================
# Debug information
# ============================================

print("\nEmbedding deployment:", embedding_deployment)
print("Chat deployment:", chat_deployment)

# ============================================
# Send question + context to LLM
# ============================================

response = llm_client.responses.create(
    model=chat_deployment,
    input=prompt
)

# ============================================
# Display response
# ============================================

print("\nResponse model:", response.model)
print("Response object:", response.object)

answer = response.output_text

print("\n================================")
print("ANSWER")
print("================================")

print(answer)