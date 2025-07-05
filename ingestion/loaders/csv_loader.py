import pandas as pd
from langchain_core.documents import Document
from typing import List

try:
    from .base import BaseLoader
except ImportError:
    from base import BaseLoader

class CSVLoader(BaseLoader):
    def __init__(self, path: str, text_cols: list[str], id_col: str | None = None):
        self.path, self.text_cols, self.id_col = self._abspath(path), text_cols, id_col

    def load(self) -> List[Document]:
        df = pd.read_csv(self.path)
        docs: List[Document] = []
        for i, (_, row) in enumerate(df.iterrows()):
            body = "\n".join(str(row[c]) for c in self.text_cols)
            row_id = str(row[self.id_col]) if self.id_col else str(i)
            docs.append(
                Document(
                    page_content=body,
                    metadata={
                        "source_type":"csv",
                        "source_path":self.path,
                        "row_index": i,
                        "doc_id": self._make_id(self.path, row_id)
                    }
                )
            )
        return docs




if __name__ == "__main__":
    import os
    
    print("=== CSV Loader Demo ===\n")
    
    # Create a demo CSV file path
    demo_csv_path = "data/raw/demo.csv"
    
    try:
        # Initialize the loader with text columns and optional ID column
        text_columns = ["title", "description", "category"]
        id_column = "id"
        
        loader = CSVLoader(demo_csv_path, text_cols=text_columns, id_col=id_column)
        print(f"Loading CSV file: {demo_csv_path}")
        print(f"Text columns: {text_columns}")
        print(f"ID column: {id_column}")
        
        # Load and process the documents
        documents = loader.load()
        
        print(f"\nSuccessfully loaded {len(documents)} document chunks:")
        print("-" * 60)
        
        for i, doc in enumerate(documents, 1):
            print(f"\nDocument {i}:")
            print(f"Content: {doc.page_content}")
            print(f"Metadata: {doc.metadata}")
            print("-" * 40)
            
    except FileNotFoundError:
        print(f"Error: Demo CSV file not found at {demo_csv_path}")
        print("Please ensure the demo.csv file exists in the data/raw folder.")
    except Exception as e:
        print(f"Error during demo: {str(e)}")
