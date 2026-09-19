import pytest
from src.ingestion.loaders import LoadedDocument
from src.ingestion.chunker import DocumentChunker

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    doc = LoadedDocument(
        document_id="doc_101",
        title="EC2 Troubleshooting Guide",
        content="Overview of EC2. " * 30,
        source="ec2_guide.md",
        service="Amazon EC2",
        category="Technical Guide",
        document_type="MD"
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.parent_doc_id == "doc_101"
        assert chunk.title == "EC2 Troubleshooting Guide"
        assert chunk.service == "Amazon EC2"
        assert chunk.metadata["source"] == "ec2_guide.md"
        assert len(chunk.content) > 0

def test_chunker_empty_document():
    chunker = DocumentChunker()
    doc = LoadedDocument(
        document_id="doc_empty",
        title="Empty Doc",
        content="",
        source="empty.txt",
        service="General AWS",
        category="Guide",
        document_type="TXT"
    )
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0
