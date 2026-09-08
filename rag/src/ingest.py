import os

from src.document_loader import load_pdf
from src.image_loader import load_image
from src.video_loader import load_video

from src.chunking import chunk_documents
from src.embeddings import create_embeddings
from src.vector_store import add_chunks


def ingest_document(file_path: str):

    print("\nStarting document ingestion...")

    file_extension = os.path.splitext(
        file_path
    )[1].lower()

    document_name = os.path.basename(file_path)

    pages = []

    # ==========================
    # PDF PROCESSING
    # ==========================

    if file_extension == ".pdf":

        print("Detected PDF file.")

        print("Extracting text from PDF...")

        pages = load_pdf(file_path)

    # ==========================
    # IMAGE PROCESSING
    # ==========================

    elif file_extension in [
        ".jpg",
        ".jpeg",
        ".png",
        ".avif",
        ".webp"
    ]:

        print("Detected image file.")

        caption = load_image(file_path)

        if caption:

            pages = [{
                "text": caption,
                "page": 1
            }]

    # ==========================
    # VIDEO PROCESSING
    # ==========================

    elif file_extension in [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv"
    ]:

        print("Detected video file.")

        description = load_video(file_path)

        if description:

            pages = [{
                "text": description,
                "page": 1
            }]

    # ==========================
    # UNSUPPORTED FILE
    # ==========================

    else:

        print(
            f"Unsupported file type: "
            f"{file_extension}"
        )

        return None

    # ==========================
    # VALIDATION
    # ==========================

    if not pages:

        raise ValueError(
            "No readable content found."
        )

    print(f"Extracted content from {len(pages)} page(s).")

    # Add file information to the extracted content
    document_name = os.path.basename(file_path)

    for page in pages:
        page["text"] = (
            f"Source file: {document_name}\n"
            f"Content: {page['text']}"
        )

    # Step 2: Chunk text
    print("Splitting content into chunks...")
    chunks = chunk_documents(pages)

    print(f"Created {len(chunks)} chunks.")

    # ==========================
    # EMBEDDINGS
    # ==========================

    print("Generating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(texts)

    # ==========================
    # CHROMADB
    # ==========================

    print("Storing vectors in ChromaDB...")

    add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_name=document_name
    )

    print("Document ingestion completed successfully!")

    return {
        "document": document_name,
        "pages": len(pages),
        "chunks": len(chunks)
    }