import os
from typing import List
from langchain_core.documents import Document
from loaders import Loaders
from loaders import OracleSQLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter



class Ingestor:
    """
    A class to ingest documents from various file sources in a directory embed them and load to a database.
    """

    def __init__(self, data_directory: str, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initializes the Ingestor with the path to the data directory.

        Args:
            data_directory (str): The path to the directory containing files to ingest.
        """
        self.data_directory = data_directory
        self.supported_extensions = {
            ".pdf": "pdf_loader",
            ".csv": "csv_loader",
            ".html": "html_loader",
        }
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def ingest_all(self) -> List[Document]:
        """
        Iterates through all files in the specified directory, loads them using the
        appropriate loader, then further splits each Document into smaller, overlapping
        chunks before returning the full list.
        """
        all_docs = []
        print(f"Scanning directory: {self.data_directory}")

        for filename in os.listdir(self.data_directory):
            filepath = os.path.join(self.data_directory, filename)
            if not os.path.isfile(filepath):
                continue

            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext in self.supported_extensions:
                print(f"-> Found supported file: {filename}")
                try:
                    loader_instance    = Loaders(filepath=filepath)
                    loader_method_name = self.supported_extensions[file_ext]
                    loader_method      = getattr(loader_instance, loader_method_name)

                    # 1) load raw Documents
                    raw_docs    = loader_method()
                    # 2) apply second‐level chunking
                    chunked_docs = self.text_splitter.split_documents(raw_docs)

                    all_docs.extend(chunked_docs)
                    print(
                        f"  - Loaded {len(raw_docs)} raw docs, "
                        f"chunked into {len(chunked_docs)} pieces from {filename}"
                    )
                except Exception as e:
                    print(f"  - ERROR loading {filename}: {e}")
            else:
                print(f"-> Skipping unsupported file: {filename}")

        return all_docs



if __name__ == "__main__":
    RAW_DATA_PATH = os.path.join("./", "data", "raw")

    ingestor = Ingestor(data_directory=RAW_DATA_PATH)
    documents = ingestor.ingest_all()

    print(f"\nTotal document chunks ingested: {len(documents)}")
    if documents:
        print(f"\n--- Sample of the first ingested document ---")
        print(documents)
