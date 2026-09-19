import sys
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from src.ingestion.ingest import IngestionPipeline
from src.vectorstore.chroma_store import ChromaVectorStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("=== Starting Data Ingestion Script ===")
    
    # Initialize pipeline and vector store
    pipeline = IngestionPipeline()
    vector_store = ChromaVectorStore()
    
    # Process sample data
    logger.info(f"Loading files from: {settings.SAMPLE_DATA_DIR}")
    docs, chunks = pipeline.process_sample_data()
    
    if not chunks:
        logger.error("No chunks generated during ingestion. Check sample data directory.")
        sys.exit(1)

    logger.info(f"Adding {len(chunks)} chunks across {len(docs)} documents to ChromaDB...")
    vector_store.add_chunks(chunks)
    
    stats = vector_store.get_stats()
    logger.info(f"=== Ingestion Complete! Vector Store Stats: {stats} ===")

if __name__ == "__main__":
    main()
