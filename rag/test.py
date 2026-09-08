import os

from src.ingest import ingest_document
from src.rag import ask_question


DATA_FOLDER = "rag/data"


SUPPORTED_EXTENSIONS = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".avif",
    ".webp",
    ".mp4",
    ".avi",
    ".mov",
    ".mkv"
)


def ingest_all_documents():
    """Ingest all supported files from the data folder."""

    for filename in os.listdir(DATA_FOLDER):

        file_path = os.path.join(DATA_FOLDER, filename)

        # Skip folders
        if not os.path.isfile(file_path):
            continue

        # Process supported files
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):

            print(f"\nProcessing: {filename}")

            result = ingest_document(file_path)

            print(result)


def chat():
    """Start RAG chat."""

    print("\nPolar Science RAG is ready!")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        response = ask_question(question)

        print("\nANSWER:")
        print(response["answer"])

        print("\nSOURCES:")

        for source in response["sources"]:

            file_type = source.get(
                "file_type",
                "PDF"
            )

            if file_type == "PDF":

                print(
                    f"📄 {source['document']} "
                    f"(Page {source['page']})"
                )

            elif file_type == "Image":

                print(
                    f"🖼️ {source['document']} "
                    f"(Image)"
                )

            elif file_type == "Video":

                print(
                    f"🎥 {source['document']} "
                    f"(Video)"
                )

            else:

                print(
                    f"- {source['document']}"
                )

        print("\n" + "=" * 60 + "\n")
        
def main():

    print("\n1. Ingest Documents")
    print("2. Start Chat")

    choice = input("\nChoose an option (1/2): ")

    if choice == "1":
        ingest_all_documents()

    elif choice == "2":
        chat()

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()