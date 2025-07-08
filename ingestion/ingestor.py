import os
from typing import List
from langchain_core.documents import Document
from loaders import Loaders
from loaders import OracleSQLLoader


class Ingestor:
    """
    A class to ingest documents from various file sources in a directory.
    """

    def __init__(self, data_directory: str):
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

    def ingest_all(self) -> List[Document]:
        """
        Iterates through all files in the specified directory, loads them using the
        appropriate loader based on file extension, and returns a list of Documents.
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
                    loader_instance = Loaders(filepath=filepath)
                    loader_method_name = self.supported_extensions[file_ext]
                    loader_method = getattr(loader_instance, loader_method_name)
                    docs = loader_method()
                    all_docs.extend(docs)
                    print(f"  - Successfully loaded {len(docs)} document chunk(s) from {filename}")
                except Exception as e:
                    print(f"  - ERROR loading {filename}: {e}")
            else:
                print(f"-> Skipping unsupported file: {filename}")

        return all_docs


if __name__ == "__main__":
    # This assumes the script is run from the project's root directory
    RAW_DATA_PATH = os.path.join("./", "data", "raw")

    ingestor = Ingestor(data_directory=RAW_DATA_PATH)
    documents = ingestor.ingest_all()

    print(f"\nTotal document chunks ingested: {len(documents)}")
    if documents:
        print(f"\n--- Sample of the first ingested document ---")
        print(documents)
        
        
    sql_loader = OracleSQLLoader(
        user="dummy_user",
        password="123456",
        dsn="localhost:1521/XEPDB1",
        query="SELECT * FROM rag_documents"
    )
    
    print(sql_loader.load())

