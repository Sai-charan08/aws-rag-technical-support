import pytest
from src.ingestion.cleaner import TextCleaner

def test_cleaner_preserves_code_blocks():
    cleaner = TextCleaner()
    raw_text = """
    # Section Header
    
    Here is some text with <script>alert('bad');</script> HTML.
    
    ```bash
    aws s3 ls s3://my-bucket --region us-east-1
    ```
    """
    cleaned = cleaner.clean(raw_text)
    assert "<script>" not in cleaned
    assert "```bash" in cleaned
    assert "aws s3 ls s3://my-bucket --region us-east-1" in cleaned

def test_cleaner_preserves_json_policies():
    cleaner = TextCleaner()
    raw_text = """
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [{"Effect": "Allow", "Action": "s3:GetObject"}]
    }
    ```
    """
    cleaned = cleaner.clean(raw_text)
    assert '"Version": "2012-10-17"' in cleaned
    assert '"Action": "s3:GetObject"' in cleaned

def test_cleaner_handles_empty_input():
    cleaner = TextCleaner()
    assert cleaner.clean("") == ""
    assert cleaner.clean(None) == ""
