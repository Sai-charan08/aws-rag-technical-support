import pytest
from src.ingestion.ingest import IngestionPipeline
from src.vectorstore.chroma_store import ChromaVectorStore
from src.retrieval.retriever import TechnicalSupportRetriever
from src.generation.llm import LLMClient
from src.rag.pipeline import RAGPipeline

@pytest.fixture(scope="module")
def setup_rag_pipeline(tmp_path_factory):
    tmp_db_path = str(tmp_path_factory.mktemp("chroma_rag_test"))
    vstore = ChromaVectorStore(persist_directory=tmp_db_path, collection_name="test_rag_col")
    ingestor = IngestionPipeline()
    docs, chunks = ingestor.process_sample_data()
    vstore.add_chunks(chunks)
    
    retriever = TechnicalSupportRetriever(vector_store=vstore, top_k=3)
    llm_client = LLMClient(provider="demo")
    return RAGPipeline(retriever=retriever, llm_client=llm_client)

def test_rag_pipeline_grounded_response(setup_rag_pipeline):
    pipeline = setup_rag_pipeline
    response = pipeline.get_rag_response("How do I fix a NoSuchBucket error?")
    
    assert "answer" in response
    assert "sources" in response
    assert "metadata" in response
    assert response["metadata"]["is_grounded"] is True
    assert len(response["sources"]) > 0

def test_rag_pipeline_ungrounded_query(setup_rag_pipeline):
    pipeline = setup_rag_pipeline
    # Ask out-of-scope query
    response = pipeline.get_rag_response("What is quantum computing teleportation protocol in physics?")
    assert "answer" in response
    assert response["metadata"]["is_grounded"] is False or len(response["sources"]) == 0
