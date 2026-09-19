import uuid
from typing import List, Dict, Any
from pydantic import BaseModel, Field
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.settings import settings
from src.ingestion.loaders import LoadedDocument
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DocumentChunk(BaseModel):
    chunk_id: str
    parent_doc_id: str
    title: str
    service: str
    category: str
    source: str
    url: str
    content: str
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentChunker:
    """Code-aware and Markdown-aware document chunker with full metadata preservation."""

    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Priority separators: Code blocks, Markdown headings, double newlines, single newlines, space
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n```\n",      # Code block boundaries
                "\n```",        # Inline code block end
                "\n## ",        # Level 2 Headings
                "\n### ",       # Level 3 Headings
                "\n\n",         # Paragraph breaks
                "\n",           # Line breaks
                " ",            # Word boundaries
                ""              # Character fallback
            ]
        )

    def chunk_document(self, doc: LoadedDocument) -> List[DocumentChunk]:
        if not doc.content or not doc.content.strip():
            return []

        raw_chunks = self.splitter.split_text(doc.content)
        total_chunks = len(raw_chunks)
        chunks = []

        for idx, text in enumerate(raw_chunks):
            chunk_id = f"{doc.document_id}_chunk_{idx}"
            chunk_meta = {
                "document_id": doc.document_id,
                "title": doc.title,
                "service": doc.service,
                "category": doc.category,
                "source": doc.source,
                "url": doc.url or "",
                "document_type": doc.document_type,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                **doc.metadata
            }

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    parent_doc_id=doc.document_id,
                    title=doc.title,
                    service=doc.service,
                    category=doc.category,
                    source=doc.source,
                    url=doc.url or "",
                    content=text.strip(),
                    chunk_index=idx,
                    total_chunks=total_chunks,
                    metadata=chunk_meta
                )
            )

        logger.debug(f"Split document '{doc.title}' into {total_chunks} chunks.")
        return chunks

    def chunk_documents(self, docs: List[LoadedDocument]) -> List[DocumentChunk]:
        all_chunks = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        logger.info(f"Total chunks generated across {len(docs)} documents: {len(all_chunks)}")
        return all_chunks
