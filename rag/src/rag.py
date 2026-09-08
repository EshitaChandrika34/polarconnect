import re

from src.retriever import retrieve_relevant_chunks
from src.prompts import SYSTEM_PROMPT, create_rag_prompt
from src.llm import generate_response


def ask_question(
    question: str,
    top_k: int = 5
):

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = retrieve_relevant_chunks(
        question,
        top_k
    )

    if not retrieved_chunks:
        return {
            "answer": "I could not find relevant information.",
            "sources": []
        }

    # Step 2: Build numbered context
    context_parts = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        file_type = chunk.get(
            "file_type",
            "PDF"
        )

        # Create appropriate source label
        if file_type == "PDF":
            location = f"Page {chunk['page']}"
        else:
            location = file_type

        label = (
            f"[Source {index}] "
            f"({chunk['source']}, {location})"
        )

        context_parts.append(
            f"{label}:\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    # Step 3: Create user prompt
    user_prompt = create_rag_prompt(
        question=question,
        context=context
    )

    # Step 4: Combine system prompt + user prompt
    full_prompt = f"""
{SYSTEM_PROMPT}

{user_prompt}
"""

    # Step 5: Generate answer from LLM
    ai_response = generate_response(full_prompt)

    # TEMPORARY DEBUG
    print("\n" + "=" * 60)
    print("RAW AI RESPONSE:")
    print("=" * 60)
    print(ai_response)
    print("=" * 60 + "\n")

    # Step 6: Find USED_SOURCES from AI response
    match = re.search(
        r"USED_SOURCES:\s*\[(.*?)\]",
        ai_response,
        re.IGNORECASE
    )

    used_numbers = []

    if match and match.group(1).strip():

        try:
            used_numbers = [
                int(number.strip())
                for number in match.group(1).split(",")
                if number.strip().isdigit()
            ]

        except ValueError:
            used_numbers = []

    # Step 7: Remove USED_SOURCES from visible answer
    clean_answer = re.sub(
        r"USED_SOURCES:\s*\[.*?\]",
        "",
        ai_response,
        flags=re.IGNORECASE
    ).strip()

    # Step 8: Build final source list
    sources = []

    seen = set()

    # If AI correctly identified sources
    if used_numbers:

        for number in used_numbers:

            index = number - 1

            if 0 <= index < len(retrieved_chunks):

                chunk = retrieved_chunks[index]

                source_key = (
                    chunk["source"],
                    chunk["page"],
                    chunk.get("file_type", "PDF")
                )

                if source_key not in seen:

                    seen.add(source_key)

                    sources.append({
                        "document": chunk["source"],
                        "page": chunk["page"],
                        "file_type": chunk.get(
                            "file_type",
                            "PDF"
                        )
                    })

    # Fallback: if AI doesn't provide source numbers
    else:

        for chunk in retrieved_chunks:

            source_key = (
                chunk["source"],
                chunk["page"],
                chunk.get("file_type", "PDF")
            )

            if source_key not in seen:

                seen.add(source_key)

                sources.append({
                    "document": chunk["source"],
                    "page": chunk["page"],
                    "file_type": chunk.get(
                        "file_type",
                        "PDF"
                    )
                })

    # Step 9: Return answer and sources
    return {
        "answer": clean_answer,
        "sources": sources
    }