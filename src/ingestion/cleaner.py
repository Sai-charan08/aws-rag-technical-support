import re
import unicodedata
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TextCleaner:
    """
    Code-aware text cleaner.
    Normalizes whitespace and HTML remnants while carefully preserving code blocks (```),
    JSON policies, CLI commands, URLs, and technical error messages.
    """

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # 1. Unicode Normalization (NFKC)
        text = unicodedata.normalize("NFKC", text)

        # 2. Extract code blocks to protect them during cleaning
        code_blocks = []
        
        def save_code_block(match):
            placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
            code_blocks.append(match.group(0))
            return placeholder

        # Protect triple-backtick code blocks
        protected_text = re.sub(r"```[\s\S]*?```", save_code_block, text)

        # Protect single-backtick inline code snippets
        inline_code_blocks = []
        def save_inline_code(match):
            placeholder = f"__INLINE_CODE_{len(inline_code_blocks)}__"
            inline_code_blocks.append(match.group(0))
            return placeholder

        protected_text = re.sub(r"`[^`\n]+`", save_inline_code, protected_text)

        # 3. Clean non-code text (strip unwanted HTML tags, normalize whitespace)
        # Remove script and style tags if present
        protected_text = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", "", protected_text, flags=re.IGNORECASE)
        # Replace non-breaking space
        protected_text = protected_text.replace("\xa0", " ").replace("\r\n", "\n")
        # Collapse multi-blank lines exceeding 3 into 2
        protected_text = re.sub(r"\n{3,}", "\n\n", protected_text)
        # Collapse multiple spaces within a line (excluding newlines)
        protected_text = re.sub(r"[ \t]+", " ", protected_text)

        # 4. Restore inline code
        for idx, inline_code in enumerate(inline_code_blocks):
            protected_text = protected_text.replace(f"__INLINE_CODE_{idx}__", inline_code)

        # 5. Restore full code blocks
        for idx, code_block in enumerate(code_blocks):
            protected_text = protected_text.replace(f"__CODE_BLOCK_{idx}__", code_block)

        return protected_text.strip()
