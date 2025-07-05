# html_loader.py
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import HTMLHeaderTextSplitter
from langchain_core.documents import Document
from typing import List

try:
    from .base import BaseLoader
except ImportError:
    from base import BaseLoader

class HTMLLoader(BaseLoader):
    def __init__(self, path: str):
        self.path = self._abspath(path)

    def load(self) -> List[Document]:
        raw_docs = UnstructuredFileLoader(self.path, mode="elements").load()
        splitter = HTMLHeaderTextSplitter(headers_to_split_on=[("h1", "header1"),
                                                               ("h2", "header2"),
                                                               ("h3", "header3")])
        docs: List[Document] = []

        for d in raw_docs:
            # splitter returns Documents too
            for chunk in splitter.split_text(d.page_content):
                docs.append(
                    Document(
                        page_content=chunk.page_content,
                        metadata={
                            "source_type": "html",
                            "source_path": self.path,
                            "header": chunk.metadata.get("header"),
                            "doc_id": self._make_id(self.path, chunk.metadata.get("header",""))
                        }
                    )
                )
        return docs



    


if __name__ == "__main__":
    import os
    print("=== HTML Loader Demo ===\n")
    
    # Create a demo HTML file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    demo_html_path = os.path.join(script_dir, "..", "..", "data", "raw", "demo.html")
    
    try:
        # Initialize the loader
        loader = HTMLLoader(demo_html_path)
        print(f"Loading HTML file: {demo_html_path}")
        
        # Load and process the documents
        documents = loader.load()
        
        print(f"\nSuccessfully loaded {len(documents)} document chunks:")
        print("-" * 50)
        
        for i, doc in enumerate(documents, 1):
            print(f"\nChunk {i}:")
            print(f"Content: {doc.page_content[:100]}...")
            print(f"Metadata: {doc.metadata}")
            print("-" * 30)
            
    except FileNotFoundError:
        print(f"Error: Demo HTML file not found at {demo_html_path}")
        print("Please ensure the demo.html file exists in the data/raw folder.")
    except Exception as e:
        print(f"Error during demo: {str(e)}")