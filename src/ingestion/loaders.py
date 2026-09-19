import os
import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger(__name__)

class LoadedDocument(BaseModel):
    document_id: str
    title: str
    content: str
    source: str
    url: Optional[str] = None
    service: str = "General AWS"
    category: str = "Technical Guide"
    document_type: str = "Markdown"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentLoader:
    """Unified loader for TXT, Markdown, PDF, HTML, JSON, CSV documents."""
    
    @staticmethod
    def infer_service_from_filename_or_content(filepath: Path, content: str) -> str:
        fname = filepath.name.lower()
        cnt_lower = content.lower()
        
        if "ec2" in fname or "instance" in fname or "ec2" in cnt_lower:
            return "Amazon EC2"
        elif "s3" in fname or "bucket" in fname or "nosuchbucket" in cnt_lower or "s3" in cnt_lower:
            return "Amazon S3"
        elif "lambda" in fname or "function" in fname or "lambda" in cnt_lower:
            return "AWS Lambda"
        elif "iam" in fname or "policy" in fname or "role" in cnt_lower or "iam" in cnt_lower:
            return "AWS IAM"
        return "General AWS Support"

    def load_file(self, filepath: Path) -> LoadedDocument:
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        ext = filepath.suffix.lower()
        content = ""
        doc_type = ext.lstrip(".")
        title = filepath.stem.replace("_", " ").replace("-", " ").title()
        
        if ext in [".md", ".markdown", ".txt"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif ext == ".json":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                content = json.dumps(data, indent=2)
        elif ext == ".html" or ext == ".htm":
            try:
                from bs4 import BeautifulSoup
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    content = soup.get_text(separator="\n")
            except Exception as e:
                logger.warning(f"Error parsing HTML with BeautifulSoup: {e}. Falling back to plain text.")
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        elif ext == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(filepath)
                pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                content = "\n\n".join(pages)
            except Exception as e:
                logger.error(f"Error reading PDF {filepath}: {e}")
                content = ""
        elif ext == ".csv":
            try:
                import pandas as pd
                df = pd.read_csv(filepath)
                content = df.to_string()
            except Exception as e:
                logger.error(f"Error reading CSV {filepath}: {e}")
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        else:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        service = self.infer_service_from_filename_or_content(filepath, content)
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(filepath.name)))
        
        return LoadedDocument(
            document_id=doc_id,
            title=title,
            content=content,
            source=filepath.name,
            url=f"https://docs.aws.amazon.com/{service.lower().replace(' ', '-')}/latest/userguide/",
            service=service,
            category="Technical Guide",
            document_type=doc_type.upper(),
            metadata={
                "filepath": str(filepath),
                "file_size_bytes": os.path.getsize(filepath)
            }
        )

    def load_directory(self, dirpath: Path) -> List[LoadedDocument]:
        dirpath = Path(dirpath)
        if not dirpath.exists() or not dirpath.is_dir():
            logger.warning(f"Directory {dirpath} does not exist or is not a directory.")
            return []
            
        supported_extensions = {".md", ".markdown", ".txt", ".json", ".html", ".htm", ".pdf", ".csv"}
        documents = []
        
        for root, _, files in os.walk(dirpath):
            for file in files:
                fpath = Path(root) / file
                if fpath.suffix.lower() in supported_extensions:
                    try:
                        doc = self.load_file(fpath)
                        if doc.content.strip():
                            documents.append(doc)
                    except Exception as e:
                        logger.error(f"Failed to load file {fpath}: {e}")
                        
        logger.info(f"Loaded {len(documents)} documents from {dirpath}")
        return documents
