import os
from typing import List, Dict, Any, Optional
from config.settings import settings
from src.retrieval.retriever import RetrievedChunk
from src.generation.prompts import SYSTEM_PROMPT_TEMPLATE, DEMO_MODE_SYNTHESIS_TEMPLATE
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LLMClient:
    """Unified LLM Client supporting OpenAI, Gemini, and Local Demo Extractive Mode."""

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

        # Automatically determine effective provider based on API keys
        if self.provider == "openai" and not self.openai_api_key:
            logger.warning("OPENAI_API_KEY is missing. Falling back to 'demo' mode.")
            self.provider = "demo"
        elif self.provider == "gemini" and not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY is missing. Falling back to 'demo' mode.")
            self.provider = "demo"

    def generate_response(self, query: str, context_chunks: List[RetrievedChunk]) -> str:
        if not context_chunks:
            return (
                "### AWS Technical Support Assistant\n\n"
                "**Status**: Information Not Found in Knowledge Base\n\n"
                "The current AWS Knowledge Base does not contain sufficient information to answer your query. "
                "Please verify your question relates to supported AWS services (EC2, S3, Lambda, IAM)."
            )

        context_str = "\n\n---\n\n".join(
            [f"[Source: {c.title} ({c.service}) - Score: {c.relevance_score:.2f}]\n{c.content}" for c in context_chunks]
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
                    {"role": "system", "content": "You are a grounded AWS technical support engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI Generation error: {e}. Falling back to demo mode.")
            return f"*(OpenAI Generation Error: {str(e)})*\n\n" + self._generate_demo_mode(query, [])

    def _generate_gemini(self, query: str, context_str: str) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.model_name or "gemini-1.5-flash")
            prompt = SYSTEM_PROMPT_TEMPLATE.format(context_str=context_str, user_query=query)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini Generation error: {e}. Falling back to demo mode.")
            return f"*(Gemini Generation Error: {str(e)})*\n\n" + self._generate_demo_mode(query, [])

    def _generate_demo_mode(self, query: str, context_chunks: List[RetrievedChunk]) -> str:
        """Synthesizes structured extractive output when no LLM API key is configured."""
        if not context_chunks:
            return (
                "Based on the current AWS Knowledge Base, sufficient relevant information was not found "
                "to answer your query."
            )

        summaries = []
        code_snippets = []

        for idx, chunk in enumerate(context_chunks[:3], 1):
            summaries.append(f"**{idx}. [{chunk.service}] {chunk.title}** (Relevance Match: `{chunk.relevance_score:.2f}`):\n{chunk.content[:350]}...")
            
            # Extract code blocks if present in chunk
            import re
            code_matches = re.findall(r"```[\s\S]*?```", chunk.content)
            for cm in code_matches:
                if cm not in code_snippets:
                    code_snippets.append(cm)

        extracted_summary = "\n\n".join(summaries)
        
        if code_snippets:
            action_plan = "The following relevant configuration / CLI code examples were retrieved from official documentation:\n\n" + "\n\n".join(code_snippets)
        else:
            action_plan = "Review the step-by-step instructions in the source documents expanded in the sidebar below."

        return DEMO_MODE_SYNTHESIS_TEMPLATE.format(
            extracted_summary=extracted_summary,
            action_plan=action_plan
        )

def get_llm_client() -> LLMClient:
    return LLMClient()
