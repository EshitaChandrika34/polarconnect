from src.embeddings import create_embedding
from src.vector_store import search_chunks


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
):

    # Convert question into embedding
    query_embedding = create_embedding(question)

    # Search ChromaDB
    results = search_chunks(
        query_embedding=query_embedding,
        top_k=top_k
    )

    retrieved_chunks = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_chunks.append({
            "text": document,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": distance
        })

    return retrieved_chunks