import os
import asyncio
import logging
from typing import List, Dict, Any, AsyncGenerator, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

class RAGService:
    """Minimal RAG service for code explanations using only Gemini"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the minimal RAG service"""
        try:
            if not self.google_api_key:
                logger.warning("GOOGLE_API_KEY not found. RAG service will use fallback mode.")
                self.initialized = True
                return
            
            # Configure Gemini
            genai.configure(api_key=self.google_api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            self.initialized = True
            logger.info("Minimal RAG service initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize RAG service, using fallback: {e}")
            self.initialized = True  # Mark as initialized even in fallback mode
    
    def is_initialized(self) -> bool:
        """Check if RAG service is initialized"""
        return self.initialized
    
    async def explain_code(self, code: str, output: str = "", error: str = "") -> str:
        """Generate code explanation"""
        try:
            if not self.model:
                return self._fallback_explanation(code, output, error)
            
            prompt = self._create_explanation_prompt(code, output, error)
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, prompt
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(code, output, error)
    
    async def explain_code_streaming(self, code: str, output: str = "", error: str = "") -> AsyncGenerator[str, None]:
        """Generate streaming code explanation"""
        try:
            if not self.model:
                yield self._fallback_explanation(code, output, error)
                return
            
            prompt = self._create_explanation_prompt(code, output, error)
            
            # Generate response and yield in chunks
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.model.generate_content, prompt
            )
            
            # Simulate streaming by splitting response into chunks
            text = response.text
            chunk_size = 50  # characters per chunk
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.05)  # Small delay for streaming effect
                    
        except Exception as e:
            logger.error(f"Error generating streaming explanation: {e}")
            yield self._fallback_explanation(code, output, error)
    
    def _create_explanation_prompt(self, code: str, output: str, error: str) -> str:
        """Create explanation prompt for Gemini"""
        prompt_parts = [
            "You are an expert programming tutor. Explain the following code in a clear, educational manner."
        ]
        
        prompt_parts.append(f"\nCode to explain:\n```\n{code}\n```")
        
        if output:
            prompt_parts.append(f"\nProgram output:\n```\n{output}\n```")
        
        if error:
            prompt_parts.append(f"\nError encountered:\n```\n{error}\n```")
            prompt_parts.append("\nPlease explain what caused this error and how to fix it.")
        else:
            prompt_parts.append("\nPlease explain how this code works, what it does, and any important concepts.")
        
        prompt_parts.append("\nProvide a helpful explanation suitable for learning.")
        
        return "\n".join(prompt_parts)
    
    def _fallback_explanation(self, code: str, output: str, error: str) -> str:
        """Fallback explanation when AI service is unavailable"""
        explanation_parts = [
            "**Code Analysis** (Fallback mode - AI service unavailable)",
            f"\n**Code:**\n```\n{code}\n```"
        ]
        
        if output:
            explanation_parts.append(f"\n**Output:**\n```\n{output}\n```")
        
        if error:
            explanation_parts.append(f"\n**Error:**\n```\n{error}\n```")
            explanation_parts.append("\n**Note:** This code encountered an error. Please check the syntax and logic.")
        else:
            explanation_parts.append("\n**Note:** This code executed successfully.")
        
        explanation_parts.append("\n**Tip:** To get detailed AI-powered explanations, please configure your GOOGLE_API_KEY environment variable.")
        
        return "\n".join(explanation_parts)
    
    async def add_documentation(self, content: str, metadata: Dict[str, Any]):
        """Placeholder for documentation addition (not implemented in minimal version)"""
        logger.info("Documentation addition not implemented in minimal mode")
        pass 