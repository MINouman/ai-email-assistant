from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from app.config import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        try:
            if settings.GROQ_API_KEY:
                self.llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.AI_MODEL,
                    temperature=0.3,
                    max_tokens=1024
                )
                logger.info("Groq LLM initialized")
            else: 
                logger.warning("No API key configured")
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")

    

    def summarize_email(self, email_content: str, subject: str = "") -> Optional[str]:
        if not self.llm:
            return None
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """
You are an expert email assistant. Summarize emails concisely. 
Rules:
    - Create a 2-3 sentence summary
    - Focus on key Points and action items
    - Be clear and professional
    - If there's a meeting or deadline, highlight it
"""), 
                ("User", "Subject: {subject}\n\nContent:\n{content}")
            ])
            chain = prompt | self.llm | StrOutputParser()

            content = email_content[:settings.MAX_EMAIL_LENGTH]

            summary = chain.invoke({
                "subject": subject,
                "content": content
            })

            return summary.strip()
        
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return None
        



    def detect_intent(self, email_content: str, subject: str = "") -> Optional[Dict]:
        if not self.llm:
            return None
        
        try: 
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Analyze the email and return JSON with:
                 - intent: One of [meeting, follow-up, information, urgent, task, social]
                 -priority: one of [high, medium, low]
                 -reasoning: brief explanation
                 
                 Return ONLY valid JSON, no markdown.
                 """),
                 ("user", "Subject: {subject}\n\nContent:\n{content}")
            ])

            chain = prompt | self.llm | JsonOutputParser()

            content = email_content[:settings.MAX_EMAIL_LENGTH]

            result = chain.invoke({
                "subject": subject, 
                "content": content
            })

            return result
        
        except Exception as e:
            logger.error(f"Intent detection error: {e}")
            return{
                "intent":"information",
                "priority": "medium",
                "reasoning": "Error in Analysis"
            }
    def extract_entities(self, email_content: str) -> Optional[Dict]:
       if not self.llm:
           return None
       try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Extract entities from the email and return JSON with:
- people: list of person names
- organizations: list of company/org names
- dates: list of mentioned dates/times
- locations: list of places
- action_items: list of tasks/todos

Return ONLY valid JSON."""),
                ("user", "{content}")
            ])
            
            chain = prompt | self.llm | JsonOutputParser()
            
            content = email_content[:settings.MAX_EMAIL_LENGTH]
            
            result = chain.invoke({"content": content})
            
            return result
       except Exception as e:
           logger.error(f"Entity extraction error: {e}")

           return {
               "people": [],
               "organizations": [],
               "dates": [],
               "locations": [],
               "action_items": []
           }

    def generate_reply_suggestions(self, email_content: str, subject: str = "") -> Optional[list]:
        if not self.llm:
            return None

        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Generate 3 quick reply options for this email.
                 Return JSON array with objects containing:
                 - text: the reply text (1-2 sectences)
                 - tone: one of [Professional, friendly, brief]
                 
                 Return ONLY valid JSON array."""),
                 ("user", "Subject: {subject}\n\nContent:\n{content}")
            ])
            chain = prompt | self.llm | JsonOutputParser()   

            content = email_content[:2000]

            result = chain.invoke({
                "subject": subject, 
                "content": content
            })

            return result
        
        except Exception as e:
            logger.error(f"Reply generator error: {e}")
            return []
        
llm_service = LLMService()