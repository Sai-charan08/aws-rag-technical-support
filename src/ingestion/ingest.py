from pathlib import Path
from typing import List, Tuple
from config.settings import settings
from src.ingestion.loaders import DocumentLoader, LoadedDocument
from src.ingestion.cleaner import TextCleaner
from src.ingestion.chunker import DocumentChunker, DocumentChunk
from src.utils.logger import get_logger

logger = get_logger(__name__)

class IngestionPipeline:
    """Orchestrates loading, cleaning, and chunking of documents."""

    def __init__(self):
        self.loader = DocumentLoader()
        self.cleaner = TextCleaner()
        self.chunker = DocumentChunker()

    def process_directory(self, data_dir: Path) -> Tuple[List[LoadedDocument], List[DocumentChunk]]:
        logger.info(f"Starting ingestion pipeline for directory: {data_dir}")
        raw_docs = self.loader.load_directory(data_dir)
        
        if not raw_docs:
            logger.warning(f"No documents found in {data_dir}")
            return [], []

        cleaned_docs = []
        for doc in raw_docs:
            cleaned_content = self.cleaner.clean(doc.content)
            doc.content = cleaned_content
            cleaned_docs.append(doc)

        chunks = self.chunker.chunk_documents(cleaned_docs)
        logger.info(f"Ingestion complete. Processed {len(cleaned_docs)} documents into {len(chunks)} chunks.")
        return cleaned_docs, chunks

    def process_sample_data(self) -> Tuple[List[LoadedDocument], List[DocumentChunk]]:
        return self.process_directory(settings.SAMPLE_DATA_DIR)
