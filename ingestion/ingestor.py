from pathlib import Path
from loaders import CustomLoader  # or from .loaders if you're running inside the same module
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_folder(folder_path: str):
    data_dir = Path(folder_path).expanduser().resolve()

    if not data_dir.exists() or not data_dir.is_dir():
        raise ValueError(f"Path is not a valid directory: {data_dir}")

    supported_exts = {
        ".pdf": "pdf_loader",     
        ".csv": "csv_loader",
        ".html": "html_loader",
        ".htm": "html_loader",
    }

    all_documents = []

    for file_path in data_dir.iterdir():
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        if ext not in supported_exts:
            logger.warning(f"Skipping unsupported file type: {file_path.name}")
            continue

        try:
            loader = CustomLoader(file_path)
            method_name = supported_exts[ext]
            method = getattr(loader, method_name)
            docs = method()  # call loader method dynamically
            all_documents.extend(docs)
            logger.info(f"Loaded {len(docs)} docs from {file_path.name}")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            continue

    logger.info(f"Loaded total {len(all_documents)} documents from folder.")
    return all_documents


if __name__ == "__main__":
    processed_data = process_folder("./data/raw")
    print(processed_data)
