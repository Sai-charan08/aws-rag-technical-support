import os
import sys
import time
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import settings
from src.rag.pipeline import get_rag_pipeline, RAGPipeline
from src.vectorstore.chroma_store import get_vector_store
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Streamlit Page Config
st.set_page_config(
    page_title="AWS Technical Support RAG Assistant",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (AWS Cloud Dark/Orange Theme)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1b2a4a 0%, #0f172a 100%);
        padding: 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-left: 6px solid #ff9900;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.4rem;
        margin-bottom: 0.8rem;
    }
    .badge {
        display: inline-block;
        background: #232f3e;
        color: #ff9900;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
        border: 1px solid #3b4252;
    }
    .status-card {
        background: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #38bdf8;
        margin-bottom: 1rem;
    }
    .source-box {
        background: #0f172a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="Initializing AWS RAG Pipeline & ChromaDB...")
def load_rag_pipeline() -> RAGPipeline:
    vector_store = get_vector_store()
    # Check if vector store is empty. If so, automatically ingest sample data
    if vector_store.count() == 0:
        logger.info("ChromaDB is empty on startup. Triggering automatic sample ingestion...")
        from src.ingestion.ingest import IngestionPipeline
        ingestor = IngestionPipeline()
        docs, chunks = ingestor.process_sample_data()
        if chunks:
            vector_store.add_chunks(chunks)
    return get_rag_pipeline()

def main():
    pipeline = load_rag_pipeline()
    vector_store = get_vector_store()

    # Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar Component
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg", width=120)
        st.title("⚙️ RAG Control Panel")

        st.subheader("📚 Knowledge Base Stats")
        stats = vector_store.get_stats()
        st.metric(label="Total Document Chunks", value=stats["total_chunks"])
        st.metric(label="Collection Status", value=stats["status"])

        st.markdown("**Supported Scope:**")
        for srv in settings.SUPPORTED_SERVICES:
            st.markdown(f"- `{srv}`")

        st.divider()

        st.subheader("🛠️ RAG Configuration")
        top_k = st.slider("Retrieval Top-K", min_value=1, max_value=10, value=settings.TOP_K)
        sim_threshold = st.slider("Similarity Threshold", min_value=0.1, max_value=0.8, value=settings.SIMILARITY_THRESHOLD, step=0.05)
        
        st.caption(f"**Embedding Model:** `{settings.EMBEDDING_MODEL_NAME}`")
        st.caption(f"**Vector Database:** `ChromaDB (Persistent)`")

        st.divider()

        st.subheader("🤖 LLM Provider Status")
        provider_name = pipeline.llm_client.provider.upper()
        if provider_name == "DEMO":
            st.warning("Mode: **Local Demo Extractive Mode**\n*(No LLM API key set in .env)*")
            with st.expander("🔑 How to set API Key"):
                st.code("OPENAI_API_KEY=your_key_here\nLLM_PROVIDER=openai", language="env")
        else:
            st.success(f"Connected: **{provider_name}** (`{pipeline.llm_client.model_name}`)")

        st.divider()

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("### 🎓 About Capstone Project")
        st.info(
            "This domain-specific RAG Technical Support Assistant retrieves authoritative "
            "AWS documentation chunks via semantic search and grounds responses to avoid hallucinating."
        )

    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1>☁️ AWS Technical Support RAG Assistant</h1>
        <p>AI-powered technical support grounded in a curated AWS Cloud Knowledge Base</p>
        <div>
            <span class="badge">Amazon EC2</span>
            <span class="badge">Amazon S3</span>
            <span class="badge">AWS Lambda</span>
            <span class="badge">AWS IAM</span>
            <span class="badge">Troubleshooting</span>
            <span class="badge">Security & Policies</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Example Query Shortcuts
    st.markdown("##### 💡 Example Questions (Click to test):")
    cols = st.columns(3)
    example_queries = [
        "How do I troubleshoot a NoSuchBucket error?",
        "What is the difference between EC2 instance types?",
        "How do I fix SSH Permission Denied on EC2?",
        "What causes AWS Lambda task execution timeouts?",
        "How does IAM least privilege work?",
        "What are S3 lifecycle policies?"
    ]

    selected_query = None
    for idx, q_text in enumerate(example_queries):
        col_idx = idx % 3
        if cols[col_idx].button(q_text, key=f"eq_{idx}", use_container_width=True):
            selected_query = q_text

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 View Supporting Source Documents & Metadata"):
                    for s_idx, src in enumerate(msg["sources"], 1):
                        st.markdown(
                            f"**{s_idx}. [{src['service']}] {src['title']}** | *Source: `{src['source']}`* | Relevance: `{src['relevance_score']:.2f}`\n"
                            f"[AWS Documentation Link]({src['url']})"
                        )

    # Handle Input from Chat or Example Button
    prompt = st.chat_input("Ask a technical AWS question (e.g. EC2 connection, S3 error, IAM policy)...")
    if selected_query:
        prompt = selected_query

    if prompt:
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant thinking & execution
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching AWS Knowledge Base & generating grounded response..."):
                start_t = time.time()
                # Update pipeline retriever settings from sidebar
                pipeline.retriever.top_k = top_k
                pipeline.retriever.similarity_threshold = sim_threshold
                
                response_data = pipeline.get_rag_response(prompt)
                answer = response_data["answer"]
                sources = response_data["sources"]
                meta = response_data["metadata"]

                # Render Answer
                st.markdown(answer)

                # Render Sources
                if sources:
                    with st.expander(f"📚 View Supporting Source Documents ({len(sources)} cited)"):
                        for s_idx, src in enumerate(sources, 1):
                            st.markdown(
                                f"**{s_idx}. [{src['service']}] {src['title']}**\n"
                                f"- **Source File:** `{src['source']}`\n"
                                f"- **Relevance Score:** `{src['relevance_score']:.2f}`\n"
                                f"- **URL:** [{src['url']}]({src['url']})\n"
                            )
                else:
                    st.warning("⚠️ No relevant source documents were found above the similarity threshold.")

                st.caption(f"⚡ *Response generated in {meta['latency_ms']} ms | Grounded: {meta['is_grounded']} | Mode: {meta['provider'].upper()}*")

        # Save Assistant Response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

if __name__ == "__main__":
    main()
