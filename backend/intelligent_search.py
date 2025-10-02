"""
Intelligent search integration for NyayaAI.

This module provides intelligent decision-making for when to use web search
versus relying on the LLM's built-in knowledge for answering legal questions.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import get_config
from search_tool import search_tool

logger = logging.getLogger(__name__)

class IntelligentSearchManager:
    """
    Manages intelligent search decisions and integration.
    
    This class determines when to use web search vs LLM knowledge
    and provides integrated responses combining both sources.
    """
    
    def __init__(self):
        """Initialize the intelligent search manager."""
        self.config = get_config()
        self.llm = None
        self.decision_chain = None
        self.synthesis_chain = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM and decision-making components."""
        try:
            # Initialize Gemini LLM with rate limiting
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.GEMINI_MODEL,
                google_api_key=self.config.GEMINI_API_KEY,
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=1024,
                convert_system_message_to_human=True,
                max_retries=3,  # Add retry logic
                request_timeout=30  # Add timeout
            )
            
            # Create decision-making prompt template
            decision_template = PromptTemplate(
                input_variables=["query"],
                template="""You are a legal AI assistant that needs to decide whether a user's legal question requires web search for the most accurate and up-to-date information.

**Your task:** Analyze the following legal question and determine if it needs web search.

**Decision Criteria - Answer YES if the query involves:**
1. **Recent legal developments** (last 2-3 years)
2. **Current case law** or recent Supreme Court/High Court judgments
3. **Recent amendments** to laws or new legislation
4. **Time-sensitive legal information** (current year)
5. **Specific case details** or recent legal news
6. **Evolving legal areas** (cyber law, data protection, etc.)
7. **Current legal procedures** or recent procedural changes
8. **Recent regulatory updates** or notifications

**Decision Criteria - Answer NO if the query involves:**
1. **Basic legal concepts** and definitions
2. **Established legal principles** from well-known cases
3. **General legal procedures** that haven't changed recently
4. **Historical legal information** (older than 3 years)
5. **Fundamental legal theories** and doctrines
6. **General legal advice** on common issues

**Query to analyze:** {query}

**Instructions:**
- Respond with only "YES" or "NO"
- If YES, also provide a brief reason (1-2 words) like "recent", "current", "amendment", etc.
- If NO, provide a brief reason like "basic", "established", "general", etc.

**Response format:** YES/NO - reason"""
            )
            
            # Create synthesis prompt template
            synthesis_template = PromptTemplate(
                input_variables=["query", "llm_response", "search_results"],
                template="""You are NyayaAI, an advanced Indian Legal AI Assistant. Your task is to enhance your initial response with current web search information to provide the most comprehensive and up-to-date legal guidance.

**Original Question:** {query}

**Your Initial Analysis:**
{llm_response}

**Current Web Information:**
{search_results}

**Enhancement Guidelines:**
• Integrate recent legal developments, amendments, or case law from the search results
• Update any outdated information with current legal positions
• Add relevant recent Supreme Court or High Court judgments
• Maintain the professional, accessible tone of your original response
• Ensure all information is accurate and properly contextualized
• If search results contradict your initial response, explain the current legal position clearly

**Response Requirements:**
• Preserve the clear structure and flow of your original response
• Seamlessly weave in new information without disrupting readability
• Maintain the educational disclaimer at the end
• Keep the response natural and conversational while remaining legally precise

**Enhanced Response:**"""
            )
            
            # Create chains
            self.decision_chain = LLMChain(
                llm=self.llm,
                prompt=decision_template,
                verbose=False
            )
            
            self.synthesis_chain = LLMChain(
                llm=self.llm,
                prompt=synthesis_template,
                verbose=False
            )
            
            logger.info("Intelligent search components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize intelligent search components: {e}")
            raise
    
    def should_search(self, query: str) -> Tuple[bool, str]:
        """
        Determine if a query requires web search.
        
        Args:
            query (str): User's legal question
            
        Returns:
            Tuple[bool, str]: (should_search, reason)
        """
        try:
            logger.info(f"Analyzing query for search decision: {query[:100]}...")
            
            # Get decision from LLM
            decision_response = self.decision_chain.run(query=query)
            
            # Parse response
            decision_response = decision_response.strip().upper()
            
            if decision_response.startswith("YES"):
                should_search = True
                reason = decision_response.split(" - ", 1)[1] if " - " in decision_response else "recent information needed"
            elif decision_response.startswith("NO"):
                should_search = False
                reason = decision_response.split(" - ", 1)[1] if " - " in decision_response else "basic legal question"
            else:
                # Fallback to conservative approach
                should_search = False
                reason = "unclear decision, defaulting to no search"
            
            logger.info(f"Search decision: {should_search} - {reason}")
            return should_search, reason
            
        except Exception as e:
            logger.error(f"Error in search decision: {e}")
            # Fallback to no search on error
            return False, "error in decision making"
    
    def intelligent_chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query with intelligent search integration.
        
        Args:
            user_input (str): User's legal question
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Enhanced response with search integration
        """
        try:
            logger.info(f"Processing intelligent chat request: {user_input[:100]}...")
            
            # Step 1: Determine if search is needed
            should_search, search_reason = self.should_search(user_input)
            
            # Step 2: Get initial LLM response
            from gemini_chain import gemini_chain
            initial_response = gemini_chain.chat(
                user_input=user_input,
                session_id=session_id
            )
            
            result = {
                "response": initial_response["response"],
                "session_id": session_id,
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp(),
                "search_decision": {
                    "should_search": should_search,
                    "reason": search_reason
                },
                "search_used": False,
                "enhanced": False
            }
            
            # Step 3: If search is needed, perform search and synthesis
            if should_search:
                logger.info("Performing web search and synthesis...")
                
                try:
                    # Perform search with timeout
                    import time
                    start_time = time.time()
                    
                    search_results = search_tool.search_and_synthesize(
                        query=user_input,
                        max_results=self.config.SEARCH_MAX_RESULTS
                    )
                    
                    # Check if search actually returned results
                    if search_results and search_results.get("search_response"):
                        # Synthesize with initial response
                        enhanced_response = self.synthesis_chain.run(
                            query=user_input,
                            llm_response=initial_response["response"],
                            search_results=search_results.get("search_response", "")
                        )
                        
                        # Update result with enhanced response
                        result.update({
                            "response": enhanced_response,
                            "search_used": True,
                            "enhanced": True,
                            "search_results": search_results,
                            "sources": search_results.get("sources", []),
                            "search_method": search_results.get("search_method", "unknown"),
                            "original_response": initial_response["response"],
                            "search_time": time.time() - start_time
                        })
                        
                        logger.info("Search and synthesis completed successfully")
                    else:
                        # Search returned no results, use original response
                        logger.warning("Search returned no results, using original response")
                        result.update({
                            "search_used": False,
                            "enhanced": False,
                            "search_note": "Search performed but no results found"
                        })
                    
                except Exception as search_error:
                    logger.error(f"Error in search/synthesis: {search_error}")
                    # Keep original response if search fails
                    result.update({
                        "search_error": str(search_error),
                        "fallback_to_original": True,
                        "search_used": False,
                        "enhanced": False
                    })
            
            logger.info("Intelligent chat request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in intelligent chat: {e}")
            raise
    
    def force_search_chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query with forced web search integration.
        
        Args:
            user_input (str): User's legal question
            session_id (str, optional): Session identifier
            
        Returns:
            Dict[str, Any]: Response with forced search integration
        """
        try:
            logger.info(f"Processing forced search chat request: {user_input[:100]}...")
            
            # Get initial LLM response
            from gemini_chain import gemini_chain
            initial_response = gemini_chain.chat(
                user_input=user_input,
                session_id=session_id
            )
            
            result = {
                "response": initial_response["response"],
                "session_id": session_id,
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp(),
                "search_decision": {
                    "should_search": True,
                    "reason": "user_requested"
                },
                "search_used": False,
                "enhanced": False
            }
            
            # Force search and synthesis
            logger.info("Performing forced web search and synthesis...")
            
            try:
                import time
                start_time = time.time()
                
                search_results = search_tool.search_and_synthesize(
                    query=user_input,
                    max_results=self.config.SEARCH_MAX_RESULTS
                )
                
                if search_results and search_results.get("search_response"):
                    # Synthesize with initial response
                    enhanced_response = self.synthesis_chain.run(
                        query=user_input,
                        llm_response=initial_response["response"],
                        search_results=search_results.get("search_response", "")
                    )
                    
                    # Update result with enhanced response
                    result.update({
                        "response": enhanced_response,
                        "search_used": True,
                        "enhanced": True,
                        "search_results": search_results,
                        "sources": search_results.get("sources", []),
                        "search_method": search_results.get("search_method", "unknown"),
                        "original_response": initial_response["response"],
                        "search_time": time.time() - start_time
                    })
                    
                    logger.info("Forced search and synthesis completed successfully")
                else:
                    logger.warning("Forced search returned no results, using original response")
                    result.update({
                        "search_used": False,
                        "enhanced": False,
                        "search_note": "Search performed but no results found"
                    })
                
            except Exception as search_error:
                logger.error(f"Error in forced search/synthesis: {search_error}")
                result.update({
                    "search_error": str(search_error),
                    "fallback_to_original": True,
                    "search_used": False,
                    "enhanced": False
                })
            
            logger.info("Forced search chat request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in forced search chat: {e}")
            raise
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global instance for the application
intelligent_search = IntelligentSearchManager()
