"""
LangChain pipeline integration with Google Gemini API.

This module provides the core LangChain functionality including:
- Gemini LLM initialization
- Conversation memory management
- Chain creation and execution
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from config import get_config

logger = logging.getLogger(__name__)

class GeminiChainManager:
    """
    Manages LangChain integration with Google Gemini API.
    
    This class handles LLM initialization, memory management,
    and chain execution for conversational AI.
    """
    
    def __init__(self):
        """Initialize the Gemini chain manager."""
        self.config = get_config()
        self.llm = None
        self.memories = {}  # Store memories by session ID
        self.conversation_chains = {}  # Store chains by session ID
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM and prompt template."""
        try:
            # Initialize Gemini LLM
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.GEMINI_MODEL,
                google_api_key=self.config.GEMINI_API_KEY,
                temperature=self.config.GEMINI_TEMPERATURE,
                max_tokens=self.config.GEMINI_MAX_TOKENS,
                convert_system_message_to_human=True
            )
            
            # Create conversation prompt template for NyayaAI
            self.prompt_template = PromptTemplate(
                input_variables=["chat_history", "input"],
                template="""You are **NyayaAI**, an advanced Indian Legal AI Assistant developed as part of the NyayaAI project. Your identity and mission combine the depth of Indian jurisprudence with the clarity and empathy of a human legal expert. You are designed to serve both legal professionals (lawyers, judges, consultants, law students) and the general public who may have little or no legal background.

            # Core Mission
            - Provide accurate, reliable, and well-structured responses to all legal queries, grounded in Indian law.
            - Act as both a **teacher and guide**: simplify law for laypersons, while offering in-depth analysis for professionals.
            - Maintain **neutrality, objectivity, and respect** in every answer.
            - Build trust by citing authoritative Indian legal sources — such as Bare Acts, the Constitution of India, and landmark Supreme Court / High Court judgments.
            - Where law is uncertain, evolving, or dependent on judicial discretion, clearly highlight such limitations.

            # Knowledge Context
            NyayaAI has been conceptualized as part of a broader ecosystem of AI-powered solutions:
            - It builds on the architecture of Google Gemini + LangChain pipeline with managed memory and session awareness.
            - It mirrors the response style of OpenAI’s GPT-5 family (me), meaning: deeply contextual, logically reasoned, natural in flow, and highly explanatory.
            - It is connected with broader project discussions such as *ArthaAI* (spiritual Hindu Q&A), *Vedatale* (AI storytelling platform), and *conflict-management simulation skits*.  
            While those projects are separate, NyayaAI’s identity is firmly legal, though it shares the same design philosophy: clarity, narrative, accessibility, and professional rigor.
            - NyayaAI is designed to scale into enterprise use-cases (consulting, compliance automation, legal research) while being people-friendly and trustworthy.

            # Core Principles of Response
            1. **Precision**: Every answer must be factually accurate and legally sound. Avoid speculation.
            2. **Clarity**: Complex concepts should first be explained simply, then expanded into professional detail.
            3. **Neutrality**: No bias toward any party, ideology, or interest group.
            4. **Accessibility**: Responses should be understandable to non-lawyers without oversimplifying.
            5. **Transparency**: Cite sources, mention when the law is ambiguous, and emphasize when professional legal consultation is necessary.

            # Response Format & Style
            Your style should mirror a highly trained legal expert who also knows how to **explain like a teacher**:
            - Begin with a **direct and clear answer** to the query in one or two sentences.
            - Then transition into structured elaboration in flowing prose (avoid bullet points unless absolutely necessary).
            - Write in **paragraphs** — natural, human-like, and engaging. Numbered lists should be rare and only for clarity (e.g., outlining statutory steps).
            - Use **mini-sections within the answer** (not as headings but as narrative shifts) to cover:
            - Legal Foundation: statutory law, constitutional provisions, and precedents.
            - Understanding the Law: explanation for non-lawyers, followed by deeper analysis for legal professionals.
            - Practical Application: how this plays out in real-life, implications, remedies, or procedures.
            - Nuances & Exceptions: highlight limitations, evolving jurisprudence, or possible conflicting views.
            - Conclude every response with a **disclaimer**:  
            "Please note: This information is for educational purposes only and does not constitute legal advice. For specific legal matters, consult a qualified legal practitioner."

            # Response Capabilities
            - Capable of answering **simple queries** (e.g., "What is Article 21 of the Constitution?") with direct, clear summaries.
            - Capable of addressing **complex analytical queries** (e.g., "How does the Supreme Court’s evolving interpretation of Article 19 impact digital free speech in India?") with layered reasoning, comparative analysis, and references.
            - Capable of **multi-turn context awareness**, remembering prior parts of the conversation, and tailoring tone to user expertise.
            - When asked questions outside Indian law, respond gracefully: either relate to comparative jurisprudence or clarify scope limitations.

            ---

            Previous Conversation:
            {chat_history}

            Question: {input}
            NyayaAI:"""
            )

            
            logger.info("Gemini chain components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini chain components: {e}")
            raise
    
    def _get_or_create_session_chain(self, session_id: Optional[str] = None):
        """Get or create a conversation chain for the given session."""
        if not session_id:
            session_id = "default"
        
        if session_id not in self.conversation_chains:
            # Create memory for this session
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=self.config.CONVERSATION_MEMORY_SIZE * 100
            )
            
            # Create conversation chain for this session
            chain = ConversationChain(
                llm=self.llm,
                memory=memory,
                prompt=self.prompt_template,
                verbose=True
            )
            
            self.memories[session_id] = memory
            self.conversation_chains[session_id] = chain
            
        return self.conversation_chains[session_id]

    def chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user chat message through the Gemini chain.
        
        Args:
            user_input (str): The user's input message
            session_id (str, optional): Session identifier for conversation tracking
            
        Returns:
            Dict[str, Any]: Response containing AI reply and metadata
        """
        try:
            logger.info(f"Processing chat request for session {session_id}: {user_input[:100]}...")
            
            # Get or create session-specific chain
            conversation_chain = self._get_or_create_session_chain(session_id)
            
            # Execute conversation chain
            response = conversation_chain.predict(input=user_input)
            
            # Get conversation history for this session
            memory = self.memories.get(session_id or "default")
            chat_history = memory.chat_memory.messages if memory else []
            
            result = {
                "response": response,
                "session_id": session_id,
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp(),
                "chat_history_length": len(chat_history)
            }
            
            logger.info("Chat request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise
    
    def chat_with_context(self, user_input: str, context: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user message with additional context.
        
        Args:
            user_input (str): The user's input message
            context (str): Additional context to include in the prompt
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Response containing AI reply and metadata
        """
        try:
            logger.info(f"Processing chat with context request: {user_input[:100]}...")
            
            # Create enhanced prompt with context and use the session-specific chain
            enhanced_input = f"Context: {context}\n\nUser Question: {user_input}"

            conversation_chain = self._get_or_create_session_chain(session_id)
            response = conversation_chain.predict(input=enhanced_input)
            
            result = {
                "response": response,
                "context_used": True,
                "session_id": session_id,
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp()
            }
            
            logger.info("Chat with context request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing chat with context request: {e}")
            raise
    
    def clear_memory(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear the conversation memory for a specific session.
        
        Args:
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Confirmation message
        """
        try:
            if not session_id:
                session_id = "default"
            
            if session_id in self.memories:
                self.memories[session_id].clear()
                logger.info(f"Memory cleared for session: {session_id}")
                
                return {
                    "message": "Conversation memory cleared successfully",
                    "session_id": session_id,
                    "timestamp": self._get_timestamp()
                }
            else:
                return {
                    "message": "No memory found for this session",
                    "session_id": session_id,
                    "timestamp": self._get_timestamp()
                }
            
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            raise
    
    def get_conversation_history(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current conversation history for a specific session.
        
        Args:
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Conversation history and metadata
        """
        try:
            if not session_id:
                session_id = "default"
            
            memory = self.memories.get(session_id)
            if not memory:
                return {
                    "conversation_history": [],
                    "session_id": session_id,
                    "message_count": 0,
                    "timestamp": self._get_timestamp()
                }
            
            messages = memory.chat_memory.messages
            history = []
            
            for message in messages:
                if isinstance(message, HumanMessage):
                    history.append({"role": "human", "content": message.content})
                elif isinstance(message, AIMessage):
                    history.append({"role": "ai", "content": message.content})
            
            return {
                "conversation_history": history,
                "session_id": session_id,
                "message_count": len(history),
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            raise
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global instance for the application
gemini_chain = GeminiChainManager()
