import chromadb
import os


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "polar_science"


_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def get_collection():

    collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Polar Science Knowledge Repository"
        }
    )

    return collection


def add_chunks(chunks, embeddings, document_name):
    """
    Store chunks, embeddings and metadata in ChromaDB.
    Avoid duplicate document ingestion.
    """

    collection = get_collection()

    # Check whether this document already exists
    existing = collection.get(
        where={"source": document_name}
    )

    # Delete old chunks if document already exists
    if existing["ids"]:
        print(
            f"Removing existing data for {document_name}..."
        )

        collection.delete(
            ids=existing["ids"]
        )

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(
            f"{document_name}_{chunk['page']}_{index}"
        )

        documents.append(chunk["text"])

        metadatas.append({
            "source": document_name,
            "page": chunk["page"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks in ChromaDB."
    )

def search_chunks(query_embedding, top_k=5):
    """
    Search for similar chunks.
    """

    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return results