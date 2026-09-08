import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


def get_llm_client():

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Check your .env file."
        )

    return Groq(api_key=api_key)


def generate_response(prompt: str):

    client = get_llm_client()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=2000
    )

    return response.choices[0].message.content