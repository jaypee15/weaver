from typing import List, AsyncIterator, Optional, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings


class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",  
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
        )
        
        # Default system prompt for bots without custom prompt
        self.default_system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
If the context doesn't contain enough information to answer the question, say "I don't know based on the available information."
Always cite the source documents when providing answers."""
    
    def build_prompt(self, query: str, context_chunks: List[dict], bot_config: Optional[Dict] = None) -> List:
        # Use bot-specific system prompt if available, otherwise use default
        if bot_config and "system_prompt" in bot_config:
            system_prompt = bot_config["system_prompt"]
        else:
            system_prompt = self.default_system_prompt
        
        context_text = "\n\n".join([
            f"[Source {i+1} - Page {chunk.get('page_num', 'N/A')}]:\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        user_prompt = f"""Context:
{context_text}

Question: {query}

Answer:"""
        
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    
    async def generate_answer(self, query: str, context_chunks: List[dict], bot_config: Optional[Dict] = None) -> str:
        try:
            messages = self.build_prompt(query, context_chunks, bot_config)
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    async def generate_answer_stream(
        self,
        query: str,
        context_chunks: List[dict],
        bot_config: Optional[Dict] = None,
    ) -> AsyncIterator[str]:
        try:
            messages = self.build_prompt(query, context_chunks, bot_config)
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            raise Exception(f"LLM streaming failed: {str(e)}")

