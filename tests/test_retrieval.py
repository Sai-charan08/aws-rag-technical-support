import pytest
from src.ingestion.ingest import IngestionPipeline
from src.vectorstore.chroma_store import ChromaVectorStore
from src.retrieval.retriever import TechnicalSupportRetriever

@pytest.fixture(scope="module")
def setup_vector_store(tmp_path_factory):
    tmp_db_path = str(tmp_path_factory.mktemp("chroma_test_db"))
    vstore = ChromaVectorStore(persist_directory=tmp_db_path, collection_name="test_collection")
    
    ingestor = IngestionPipeline()
    docs, chunks = ingestor.process_sample_data()
    vstore.add_chunks(chunks)
    return vstore

def test_retriever_returns_results(setup_vector_store):
    vstore = setup_vector_store
    retriever = TechnicalSupportRetriever(vector_store=vstore, top_k=3)
    
    results = retriever.retrieve("How do I fix NoSuchBucket error in S3?")
    assert len(results) > 0
    top_chunk = results[0]
    assert "S3" in top_chunk.service or "NoSuchBucket" in top_chunk.content or "S3" in top_chunk.content
    assert top_chunk.relevance_score >= 0.0

def test_retriever_filter_threshold(setup_vector_store):
    vstore = setup_vector_store
    retriever = TechnicalSupportRetriever(vector_store=vstore, top_k=5, similarity_threshold=0.3)
    
    results = retriever.retrieve("Permission denied publickey SSH EC2")
    filtered = retriever.filter_relevant_chunks(results)
    assert len(filtered) <= len(results)
    for chunk in filtered:
        assert chunk.relevance_score >= 0.3
