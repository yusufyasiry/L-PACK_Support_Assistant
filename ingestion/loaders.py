import logging
from pathlib import Path
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_core.documents import Document
from typing import List
from langdetect import detect
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_core.documents import Document
import csv




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomLoader:
    def __init__(self, path: str | Path):
        """Initialize the CustomLoader with a file path.
        
        Args:
            path: Path to the file to be loaded
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is invalid
        """
        try:
            self.path = Path(path).expanduser().resolve()
            
            # Validate that the file exists
            if not self.path.exists():
                raise FileNotFoundError(f"File not found: {self.path}")
            
            # Validate that it's a file, not a directory
            if not self.path.is_file():
                raise ValueError(f"Path is not a file: {self.path}")
                
            logger.info(f"Initialized CustomLoader with path: {self.path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CustomLoader with path {path}: {str(e)}")
            raise

    def pdf_loader(self) -> List[Document]:
        """Load and process PDF documents.
        
        Returns:
            List of processed Document objects
            
        Raises:
            ImportError: If required dependencies are missing
            FileNotFoundError: If the PDF file cannot be accessed
            ValueError: If the PDF file is corrupted or invalid
            Exception: For other unexpected errors
        """
        try:
            # Check if the file is a PDF
            if self.path.suffix.lower() != '.pdf':
                raise ValueError(f"File is not a PDF: {self.path}")
            
            logger.info(f"Loading PDF: {self.path}")
            
            # Attempt to load the PDF
            try:
                loader = UnstructuredPDFLoader(str(self.path), mode="elements")
                docs = loader.load()
            except ImportError as e:
                logger.error(f"Missing required dependencies for PDF loading: {str(e)}")
                raise ImportError(f"Please install required dependencies: pip install unstructured")
            except Exception as e:
                logger.error(f"Failed to load PDF {self.path}: {str(e)}")
                raise ValueError(f"Failed to load PDF file: {str(e)}")
            
            if not docs:
                logger.warning(f"No content extracted from PDF: {self.path}")
                return []
            
            logger.info(f"Successfully loaded {len(docs)} chunks from PDF")
            
            # Process each document
            processed_docs = []
            for i, doc in enumerate(docs):
                try:
                    # page_number is already provided by Unstructured; keep it if present
                    page = doc.metadata.get("page_number", 0)
                    content = doc.page_content.strip()
                    lang = detect(content) if content else "und"
                    
                    # Update metadata with additional information
                    doc.metadata |= {
                        "source_type": "pdf",
                        "source_path": str(self.path),
                        "doc_id": f"{self.path.stem}_p{page}_chunk{i}",
                        "chunk_index": i,
                        "total_chunks": len(docs),
                        "languages": lang
                    }
                    
                    processed_docs.append(doc)
                    
                except Exception as e:
                    logger.warning(f"Failed to process chunk {i} from {self.path}: {str(e)}")
                    # Continue processing other chunks even if one fails
                    continue
            
            logger.info(f"Successfully processed {len(processed_docs)} out of {len(docs)} chunks")
            return processed_docs
            
        except Exception as e:
            logger.error(f"PDF loading failed for {self.path}: {str(e)}")
            raise
        
    def csv_loader(self) -> List[Document]:
        documents = []
        try:
            with self.path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    try:
                        content = "\n".join(f"{k}: {v}" for k, v in row.items() if v is not None).strip()
                        lang = detect(content) if content else "und"

                        doc = Document(
                            page_content=content,
                            metadata={
                                "source_type": "csv",
                                "source_path": str(self.path),
                                "row_index": idx,
                                "columns": list(row.keys()),
                                "language": lang
                            }
                        )
                        documents.append(doc)
                    except Exception as e:
                        logger.warning(f"Failed to process row {idx}: {str(e)}")
                        continue

            logger.info(f"Successfully loaded {len(documents)} rows from CSV")
            return documents

        except Exception as e:
            logger.error(f"Error reading CSV {self.path}: {str(e)}")
            raise
    
    def html_loader(self) -> List[Document]:
        try:
            loader = UnstructuredHTMLLoader(str(self.path), mode="elements")
            raw_elements = loader.load()

            grouped_docs = []
            current_chunk = ""
            current_metadata = {}
            chunk_counter = 0

            for i, element in enumerate(raw_elements):
                # Unstructured’s semantic category (e.g. Title, Heading, ListItem …)
                tag = element.metadata.get("category", "UncategorizedText")
                text = element.page_content.strip()
                if not text:
                    continue  # skip empty elements

                element.metadata["html_tag"] = tag  # keep tag in element’s own metadata

                # Start a new chunk whenever we hit a heading/title element
                if tag.startswith("Title") or tag.startswith("Heading"):
                    if current_chunk:
                        lang = detect(current_chunk)
                        grouped_docs.append(
                            Document(
                                page_content=current_chunk.strip(),
                                metadata={
                                    **current_metadata,
                                    "chunk_index": chunk_counter,
                                    "source_type": "html",
                                    "source_path": str(self.path),
                                    "language": lang,
                                },
                            )
                        )
                        chunk_counter += 1

                    current_chunk = f"{text}\n"
                    current_metadata = {"html_tag": tag, "element_index": i}
                else:
                    current_chunk += f"{text}\n"

            # Flush the final chunk
            if current_chunk.strip():
                lang = detect(current_chunk)
                grouped_docs.append(
                    Document(
                        page_content=current_chunk.strip(),
                        metadata={
                            **current_metadata,
                            "chunk_index": chunk_counter,
                            "source_type": "html",
                            "source_path": str(self.path),
                            "language": lang,
                        },
                    )
                )

            logger.info(f"Grouped and loaded {len(grouped_docs)} HTML sections")
            return grouped_docs

        except Exception as e:
            logger.error(f"Failed to load HTML {self.path}: {str(e)}")
            raise
        
        


