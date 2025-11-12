from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings


class PromptGeneratorService:
    """Generates optimal system prompts from business information using LLM"""
    
    def __init__(self):
        # Use fast model for prompt generation
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,  # Slightly higher for creativity
        )
    
    async def generate_from_business_info(
        self,
        business_name: str,
        industry: str,
        description: str,
        tone: str,
        primary_goal: str,
        special_instructions: Optional[str] = None,
    ) -> str:
        """Generate a system prompt tailored to the business"""
        
        # Map tone to specific instructions
        tone_guidelines = {
            "professional": "professional, polished, and business-appropriate",
            "friendly": "warm, conversational, and approachable",
            "technical": "precise, detailed, and technically accurate",
            "casual": "relaxed, informal, and easy-going",
            "formal": "formal, academic, and authoritative",
        }
        
        tone_description = tone_guidelines.get(tone, "professional")
        
        # Meta-prompt for generating the system prompt
        meta_prompt = f"""You are an expert at writing system prompts for AI chatbots. 

Given the following business information, create an optimal system prompt that will guide an AI assistant to respond perfectly for this business.

**Business Information:**
- Business Name: {business_name}
- Industry: {industry}
- What they do: {description}
- Desired Tone: {tone_description}
- Primary Goal: {primary_goal}
{f"- Special Instructions: {special_instructions}" if special_instructions else ""}

**Requirements for the system prompt:**
1. Define the AI's role clearly (e.g., "You are {business_name}'s AI assistant")
2. Specify the tone: {tone_description}
3. Explain the primary goal: {primary_goal}
4. Include guidelines for answering based on provided context
5. Specify how to handle questions without sufficient context
6. Include any relevant disclaimers or limitations
7. Encourage citing sources when appropriate
{f"8. Incorporate these special instructions: {special_instructions}" if special_instructions else ""}

**Output Format:**
Write ONLY the system prompt itself (2-4 paragraphs), ready to be used directly. Do not include any meta-commentary, explanations, or markdown formatting. Start with "You are..." and write in second person.

Generate the system prompt now:"""

        messages = [
            SystemMessage(content="You are an expert system prompt engineer. You write clear, effective prompts that guide AI assistants to behave optimally for specific businesses."),
            HumanMessage(content=meta_prompt),
        ]
        
        response = await self.llm.ainvoke(messages)
        system_prompt = response.content.strip()
        
        # Clean up any markdown or extra formatting
        system_prompt = system_prompt.replace("```", "").strip()
        
        return system_prompt

