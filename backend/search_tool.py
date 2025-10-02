"""
Online search tool integration using LangChain.

This module provides search capabilities using LangChain's community tools
for retrieving external knowledge and integrating it with Gemini responses.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import get_config

logger = logging.getLogger(__name__)

class SearchToolManager:
    """
    Manages online search functionality using LangChain tools.
    
    This class provides search capabilities and integrates search results
    with Gemini LLM for comprehensive responses.
    """
    
    def __init__(self):
        """Initialize the search tool manager."""
        self.config = get_config()
        self.search_tool = None
        self.llm = None
        self.search_agent = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize search tools and LLM components."""
        try:
            # Initialize Gemini LLM for search integration
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.GEMINI_MODEL,
                google_api_key=self.config.GEMINI_API_KEY,
                temperature=self.config.GEMINI_TEMPERATURE,
                max_tokens=self.config.GEMINI_MAX_TOKENS,
                convert_system_message_to_human=True
            )
            
            # Initialize DuckDuckGo search tool with retry logic
            self.search_tool = DuckDuckGoSearchRun()
            
            # Add fallback search methods
            self.search_methods = [
                self._search_duckduckgo,
                self._search_fallback,
                self._search_simple
            ]
            
            # Create search tools list
            tools = [
                Tool(
                    name="DuckDuckGo Search",
                    description="Search for current information on the internet. "
                               "Use this tool when you need to find recent or specific information "
                               "that might not be in your training data.",
                    func=self.search_tool.run
                )
            ]
            
            # Initialize search agent
            self.search_agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            logger.info("Search tool components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize search tool components: {e}")
            raise
    
    def search_and_synthesize(self, query: str, max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for information and synthesize results using Gemini.
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of search results
            
        Returns:
            Dict[str, Any]: Search results with synthesized response
        """
        try:
            logger.info(f"Processing search request: {query[:100]}...")
            
            # Use robust search with fallbacks
            search_data = self._robust_search(query)
            
            result = {
                "query": query,
                "search_response": search_data.get("content", ""),
                "sources": search_data.get("sources", []),
                "search_method": search_data.get("search_method", "unknown"),
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp(),
                "search_used": True
            }
            
            logger.info("Search request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing search request: {e}")
            raise
    
    def simple_search(self, query: str, max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform a simple search without LLM synthesis.
        
        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results
            
        Returns:
            Dict[str, Any]: Raw search results
        """
        try:
            logger.info(f"Processing simple search request: {query[:100]}...")
            
            # Perform robust search
            search_data = self._robust_search(query)
            
            result = {
                "query": query,
                "search_results": search_data.get("content", ""),
                "sources": search_data.get("sources", []),
                "search_method": search_data.get("search_method", "unknown"),
                "timestamp": self._get_timestamp(),
                "search_type": "simple"
            }
            
            logger.info("Simple search request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing simple search request: {e}")
            raise
    
    def search_with_context(self, query: str, context: str, max_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Search with additional context for more targeted results.
        
        Args:
            query (str): Search query
            context (str): Additional context to refine the search
            max_results (int, optional): Maximum number of results
            
        Returns:
            Dict[str, Any]: Contextual search results
        """
        try:
            logger.info(f"Processing contextual search request: {query[:100]}...")
            
            # Create enhanced query with context
            enhanced_query = f"Context: {context}\n\nSearch for: {query}"
            
            # Use search agent with enhanced query
            search_response = self.search_agent.run(enhanced_query)
            
            result = {
                "query": query,
                "context": context,
                "search_response": search_response,
                "model": self.config.GEMINI_MODEL,
                "timestamp": self._get_timestamp(),
                "contextual_search": True
            }
            
            logger.info("Contextual search request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing contextual search request: {e}")
            raise
    
    def multi_query_search(self, queries: List[str], synthesize: bool = True) -> Dict[str, Any]:
        """
        Perform multiple searches and optionally synthesize results.
        
        Args:
            queries (List[str]): List of search queries
            synthesize (bool): Whether to synthesize results with LLM
            
        Returns:
            Dict[str, Any]: Combined search results
        """
        try:
            logger.info(f"Processing multi-query search with {len(queries)} queries")
            
            all_results = []
            
            for i, query in enumerate(queries):
                logger.info(f"Processing query {i+1}/{len(queries)}: {query[:50]}...")
                
                if synthesize:
                    result = self.search_and_synthesize(query)
                else:
                    result = self.simple_search(query)
                
                all_results.append({
                    "query_index": i + 1,
                    "query": query,
                    "result": result
                })
            
            # If synthesis is requested, combine all results
            if synthesize and len(queries) > 1:
                combined_prompt = f"""Based on the following search results from multiple queries, 
                provide a comprehensive synthesis:

                {[r['result'].get('search_response', r['result'].get('search_results', '')) for r in all_results]}

                Please synthesize these results into a coherent response."""
                
                synthesis = self.llm.predict(combined_prompt)
                
                result = {
                    "queries": queries,
                    "individual_results": all_results,
                    "synthesis": synthesis,
                    "timestamp": self._get_timestamp(),
                    "multi_query": True
                }
            else:
                result = {
                    "queries": queries,
                    "results": all_results,
                    "timestamp": self._get_timestamp(),
                    "multi_query": True
                }
            
            logger.info("Multi-query search processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing multi-query search: {e}")
            raise
    
    def _search_duckduckgo(self, query: str) -> Dict[str, Any]:
        """Primary DuckDuckGo search method with source extraction."""
        try:
            search_results = self.search_tool.run(query)
            
            # Try to extract sources from the search results
            sources = self._extract_sources_from_text(search_results)
            
            return {
                "content": search_results,
                "sources": sources,
                "search_method": "duckduckgo"
            }
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            raise
    
    def _search_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback search method using web scraping."""
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            
            # Use a different search approach
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results with sources
            results = []
            sources = []
            
            for result in soup.find_all('div', class_='g')[:3]:  # Get top 3 results
                title_elem = result.find('h3')
                desc_elem = result.find('span', class_='aCOpRe')
                link_elem = result.find('a')
                
                if title_elem and desc_elem:
                    title = title_elem.get_text()
                    description = desc_elem.get_text()
                    results.append(f"{title}: {description}")
                    
                    # Extract URL if available
                    if link_elem and link_elem.get('href'):
                        url = link_elem.get('href')
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        sources.append({
                            "title": title,
                            "url": url,
                            "description": description
                        })
            
            return {
                "content": "\n".join(results) if results else "No search results found",
                "sources": sources,
                "search_method": "google_fallback"
            }
            
        except Exception as e:
            logger.warning(f"Fallback search failed: {e}")
            raise
    
    def _search_simple(self, query: str) -> Dict[str, Any]:
        """Simple fallback that returns a basic response."""
        return {
            "content": f"Search query: {query}\nNote: Web search temporarily unavailable. Using AI knowledge only.",
            "sources": [],
            "search_method": "fallback"
        }
    
    def _extract_sources_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract source URLs from search result text."""
        import re
        
        sources = []
        # Look for URLs in the text
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        for i, url in enumerate(urls[:5]):  # Limit to 5 sources
            # Try to extract title from surrounding text
            title = f"Source {i+1}"
            sources.append({
                "title": title,
                "url": url,
                "description": "Web search result"
            })
        
        return sources

    def _robust_search(self, query: str) -> Dict[str, Any]:
        """Robust search with multiple fallback methods."""
        for i, method in enumerate(self.search_methods):
            try:
                logger.info(f"Trying search method {i+1}/{len(self.search_methods)}")
                result = method(query)
                if isinstance(result, dict):
                    if result.get("content") and len(result["content"].strip()) > 10:
                        logger.info(f"Search method {i+1} succeeded")
                        return result
                elif isinstance(result, str) and len(result.strip()) > 10:
                    logger.info(f"Search method {i+1} succeeded")
                    return {
                        "content": result,
                        "sources": [],
                        "search_method": f"method_{i+1}"
                    }
            except Exception as e:
                logger.warning(f"Search method {i+1} failed: {e}")
                continue
        
        # If all methods fail, return a basic response
        logger.error("All search methods failed, using fallback")
        return self._search_simple(query)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global instance for the application
search_tool = SearchToolManager()
