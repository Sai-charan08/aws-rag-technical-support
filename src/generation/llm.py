import os
import re
from typing import List, Dict, Any, Optional
from config.settings import settings
from src.retrieval.retriever import RetrievedChunk
from src.generation.prompts import SYSTEM_PROMPT_TEMPLATE
from src.models.solution_model import get_solution_model
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LLMClient:
    """Unified LLM Client providing direct, concise suitable solutions without extraneous text."""

    def __init__(
        self,
        provider: str = settings.LLM_PROVIDER,
        model_name: str = settings.LLM_MODEL,
        openai_api_key: str = settings.OPENAI_API_KEY,
        gemini_api_key: str = settings.GEMINI_API_KEY
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        self.gemini_api_key = gemini_api_key
        self.solution_model = get_solution_model()

        # Automatically determine effective provider based on API keys
        if self.provider == "openai" and not self.openai_api_key:
            logger.warning("OPENAI_API_KEY is missing. Falling back to 'demo' mode.")
            self.provider = "demo"
        elif self.provider == "gemini" and not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY is missing. Falling back to 'demo' mode.")
            self.provider = "demo"

        if self.provider == "gemini" and (not self.model_name or "gpt" in self.model_name.lower()):
            self.model_name = "gemini-1.5-flash"

    def generate_response(self, query: str, context_chunks: List[RetrievedChunk]) -> str:
        # First check the trained Solution Model for direct suitable answer
        exact_match = self.solution_model.get_exact_solution(query)
        if exact_match:
            return exact_match

        if not context_chunks:
            return (
                "Based on the current AWS Knowledge Base, sufficient information is not available "
                "to answer this specific query. Please ensure your request targets Amazon EC2, S3, Lambda, or IAM."
            )

        context_str = "\n\n---\n\n".join(
            [f"[Source: {c.title} ({c.service})]\n{c.content}" for c in context_chunks]
        )

        if self.provider == "openai":
            return self._generate_openai(query, context_str)
        elif self.provider == "gemini":
            return self._generate_gemini(query, context_str)
        else:
            return self._generate_demo_mode(query, context_chunks)

    def _generate_openai(self, query: str, context_str: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            prompt = SYSTEM_PROMPT_TEMPLATE.format(context_str=context_str, user_query=query)
            
            response = client.chat.completions.create(
                model=self.model_name or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a direct, precise AWS Technical Support Engineer. Provide only the suitable solution without boilerplate or filler."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI Generation error: {e}. Falling back to direct extraction mode.")
            return self._generate_demo_mode(query, [])

    def _generate_gemini(self, query: str, context_str: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_api_key)
        prompt = SYSTEM_PROMPT_TEMPLATE.format(context_str=context_str, user_query=query)

        candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini model '{model_name}' failed: {e}")

        return self._generate_demo_mode(query, [])

    def _generate_demo_mode(self, query: str, context_chunks: List[RetrievedChunk]) -> str:
        """Extracts direct, suitable technical solutions without extraneous meta-content."""
        # 1. Check trained solution model
        direct = self.solution_model.get_exact_solution(query)
        if direct:
            return direct

        if not context_chunks:
            return (
                "Based on the current AWS Knowledge Base, sufficient information was not found "
                "to resolve this request. Please specify the AWS service (EC2, S3, Lambda, IAM) and error message."
            )

        # 2. Extract solution sections and code blocks from retrieved chunks
        solution_blocks = []
        code_blocks = []

        for chunk in context_chunks[:2]:
            content = chunk.content.strip()
            # Extract code snippets
            matches = re.findall(r"```[\s\S]*?```", content)
            for m in matches:
                if m not in code_blocks:
                    code_blocks.append(m)
            
            # Clean section headers
            lines = [l for l in content.split("\n") if not l.startswith("# ")]
            cleaned_text = "\n".join(lines[:12])
            if cleaned_text:
                solution_blocks.append(cleaned_text)

        output_parts = ["Hello! I'd be glad to help you resolve this. Here is the step-by-step solution based on AWS documentation:\n"]
        if solution_blocks:
            output_parts.append(solution_blocks[0])
        if code_blocks:
            output_parts.append("\n**Applicable Command / Code:**\n" + "\n\n".join(code_blocks[:2]))
        output_parts.append("\nPlease let me know if you need any further assistance with this!")

        return "\n\n".join(output_parts)

def get_llm_client() -> LLMClient:
    return LLMClient()
