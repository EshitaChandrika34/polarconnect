from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(pages, chunk_size=1000, chunk_overlap=200):
    """
    Split PDF pages into smaller chunks while
    preserving page metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for page_data in pages:

        page_text = page_data["text"]
        page_number = page_data["page"]

        text_chunks = splitter.split_text(page_text)

        for chunk in text_chunks:
            chunks.append({
                "text": chunk,
                "page": page_number
            })

    return chunks