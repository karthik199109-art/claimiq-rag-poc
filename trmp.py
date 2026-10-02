import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

print("Endpoint:", endpoint)
print("Deployment:", deployment)

client = OpenAI(
    api_key=api_key,
    base_url=f"{endpoint.rstrip('/')}/openai/v1/",
)

response = client.responses.create(
    model=deployment,
    input="Reply with exactly: Hello from ClaimIQ",
    max_output_tokens=50,
)

print("Response model:", response.model)
print("Response object:", response.object)
print("Answer:", response.output_text)