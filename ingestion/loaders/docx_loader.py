from langchain_unstructured import UnstructuredLoader
from langchain_core.documents import Document
from typing import List

try:
    from .base import BaseLoader
except ImportError:
    from base import BaseLoader

class DocxLoader(BaseLoader):
    def __init__(self, path: str):
        self.path = self._abspath(path)

    def load(self) -> List[Document]:
        loader = UnstructuredLoader(self.path, mode="elements")
        docs = loader.load()
        for d in docs:
            d.metadata |= {
                "source_type": "docx",
                "source_path": self.path,
                "doc_id": self._make_id(self.path, str(d.metadata.get("page_number")))
            }
        return docs
    
    
if __name__ == "__main__":
    # Test the DOCXLoader
    import os
    # Get the path to the docx file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docx_path = os.path.join(script_dir, "..", "..", "data", "raw", "Test_document.docx")
    
    try:
        loader = DocxLoader(docx_path)
        docs = loader.load()
        print(f"Successfully loaded {len(docs)} documents from DOCX")
        for i, doc in enumerate(docs[:10]):  # Show first 10 documents
            print(f"Document {i+1}: {doc.page_content[:100]}...")
    except Exception as e:
        print(f"Error loading DOCX: {e}")
