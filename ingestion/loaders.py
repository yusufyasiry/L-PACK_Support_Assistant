from langchain_community.document_loaders import UnstructuredCSVLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from typing import List
from langchain_core.documents import Document
import oracledb


class Loaders:
    def __init__(self, filepath):
        self.filepath = filepath

    def csv_loader(self):
        """Loads data from a CSV file, using UTF-8 encoding."""
        loader = UnstructuredCSVLoader(
            file_path=self.filepath, mode="elements", encoding="utf-8"
        )
        docs = loader.load()
        return docs

    def pdf_loader(self):
        """Loads data from a PDF file."""
        loader = UnstructuredPDFLoader(file_path=self.filepath, mode="elements")
        docs = loader.load()
        return docs

    def html_loader(self):
        """Loads data from an HTML file."""
        loader = UnstructuredHTMLLoader(file_path=self.filepath, mode="elements")
        docs = loader.load()
        return docs
    
class OracleSQLLoader:
    def __init__(self, user ="dummy_user", password ="123456", dsn="localhost:1521/XEPDB1", query ="SELECT * FROM rag_documents"):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.query = query

    def load(self) -> List[Document]:
        connection = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
        cursor = connection.cursor()
        cursor.execute(self.query)

        columns = [col[0] for col in cursor.description]
        documents = []

        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            text_content = "\n".join(f"{k}: {v}" for k, v in row_dict.items() if v is not None)

            doc = Document(
                page_content=text_content,
                metadata={
                    "source_type": "oracle_sql",
                    "query": self.query,
                    "row_id": row_dict.get("id") or row_dict.get("ID") or None,
                }
            )
            documents.append(doc)

        cursor.close()
        connection.close()
        return documents

