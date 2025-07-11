import os
import asyncio
import logging
from typing import List, Dict, Any, AsyncGenerator, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
import google.generativeai as genai

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval-Augmented Generation service for code explanations"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
        # Initialize components
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.text_splitter = None
        self.initialized = False
        
        # Configuration
        self.chunk_size = 500
        self.chunk_overlap = 50
        self.max_retrieved_docs = 5
        
    async def initialize(self):
        """Initialize the RAG service components"""
        try:
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")
            
            # Configure Gemini
            genai.configure(api_key=self.google_api_key)
            
            # Initialize embeddings
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                api_key=self.google_api_key,
                temperature=0.1,
                max_tokens=2048
            )
            
            # Initialize vector store
            await self._initialize_vectorstore()
            
            # Load default documentation if empty
            if self._is_vectorstore_empty():
                await self._load_default_documentation()
            
            self.initialized = True
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if RAG service is initialized"""
        return self.initialized
    
    async def _initialize_vectorstore(self):
        """Initialize Chroma vector store"""
        try:
            # Create Chroma client
            client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Initialize Chroma vector store
            self.vectorstore = Chroma(
                client=client,
                collection_name="code_documentation",
                embedding_function=self.embeddings,
                persist_directory=self.chroma_persist_directory
            )
            
            logger.info("Vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def _is_vectorstore_empty(self) -> bool:
        """Check if vector store is empty"""
        try:
            collection = self.vectorstore._collection
            return collection.count() == 0
        except:
            return True
    
    async def _load_default_documentation(self):
        """Load default programming documentation"""
        try:
            logger.info("Loading default documentation...")
            
            # Python documentation
            python_docs = [
                {
                    "content": """
                    Python Basics:
                    - print() function displays output to console
                    - Variables don't need type declaration
                    - Indentation is significant for code blocks
                    - Comments start with #
                    
                    Common errors:
                    - IndentationError: Check consistent spacing/tabs
                    - NameError: Variable not defined before use
                    - SyntaxError: Invalid Python syntax
                    - TypeError: Operation on incompatible types
                    """,
                    "metadata": {"language": "python", "type": "basics"}
                },
                {
                    "content": """
                    Python Data Types:
                    - int: Integer numbers (1, 42, -5)
                    - float: Decimal numbers (3.14, -2.5)
                    - str: Text strings ("hello", 'world')
                    - list: Ordered collections [1, 2, 3]
                    - dict: Key-value pairs {"key": "value"}
                    - bool: True or False values
                    
                    Type conversion:
                    - int("123") converts string to integer
                    - str(456) converts number to string
                    - float("3.14") converts string to float
                    """,
                    "metadata": {"language": "python", "type": "data_types"}
                },
                {
                    "content": """
                    Python Control Flow:
                    - if/elif/else: Conditional execution
                    - for loops: Iterate over sequences
                    - while loops: Repeat while condition is true
                    - break: Exit loop early
                    - continue: Skip to next iteration
                    
                    Example:
                    for i in range(5):
                        if i == 2:
                            continue
                        print(i)
                    """,
                    "metadata": {"language": "python", "type": "control_flow"}
                }
            ]
            
            # JavaScript documentation
            javascript_docs = [
                {
                    "content": """
                    JavaScript Basics:
                    - console.log() displays output to console
                    - Variables: var, let, const
                    - Semicolons recommended but optional
                    - Comments: // for single line, /* */ for multi-line
                    
                    Common errors:
                    - ReferenceError: Variable not declared
                    - TypeError: Wrong type for operation
                    - SyntaxError: Invalid JavaScript syntax
                    - RangeError: Number out of valid range
                    """,
                    "metadata": {"language": "javascript", "type": "basics"}
                },
                {
                    "content": """
                    JavaScript Data Types:
                    - number: Both integers and floats (42, 3.14)
                    - string: Text data ("hello", 'world', `template`)
                    - boolean: true or false
                    - array: Ordered lists [1, 2, 3]
                    - object: Key-value pairs {key: "value"}
                    - null: Intentional absence of value
                    - undefined: Variable declared but not assigned
                    
                    Type conversion:
                    - Number("123") converts to number
                    - String(456) converts to string
                    - Boolean(value) converts to boolean
                    """,
                    "metadata": {"language": "javascript", "type": "data_types"}
                },
                {
                    "content": """
                    JavaScript Control Flow:
                    - if/else if/else: Conditional execution
                    - for loops: Traditional and for...of loops
                    - while loops: Repeat while condition is true
                    - break: Exit loop early
                    - continue: Skip to next iteration
                    
                    Example:
                    for (let i = 0; i < 5; i++) {
                        if (i === 2) continue;
                        console.log(i);
                    }
                    """,
                    "metadata": {"language": "javascript", "type": "control_flow"}
                }
            ]
            
            # Combine all documentation
            all_docs = python_docs + javascript_docs
            
            # Process and add to vector store
            documents = []
            for doc in all_docs:
                # Split large documents
                chunks = self.text_splitter.split_text(doc["content"])
                for chunk in chunks:
                    if chunk.strip():
                        documents.append(Document(
                            page_content=chunk,
                            metadata=doc["metadata"]
                        ))
            
            # Add to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                logger.info(f"Loaded {len(documents)} documentation chunks")
            
        except Exception as e:
            logger.error(f"Failed to load default documentation: {e}")
    
    async def add_documentation(self, content: str, metadata: Dict[str, Any]):
        """Add new documentation to the vector store"""
        try:
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            documents = []
            for chunk in chunks:
                if chunk.strip():
                    documents.append(Document(
                        page_content=chunk,
                        metadata=metadata
                    ))
            
            # Add to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                logger.info(f"Added {len(documents)} new documentation chunks")
            
        except Exception as e:
            logger.error(f"Failed to add documentation: {e}")
            raise
    
    async def explain_code(self, code: str, output: str = "", error: str = "") -> str:
        """Generate complete code explanation"""
        try:
            if not self.initialized:
                raise ValueError("RAG service not initialized")
            
            # Create query for retrieval
            query = self._create_query(code, output, error)
            
            # Retrieve relevant documentation
            docs = await self._retrieve_relevant_docs(query)
            
            # Generate explanation
            explanation = await self._generate_explanation(code, output, error, docs)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Failed to explain code: {e}")
            return f"Sorry, I couldn't explain the code due to an error: {str(e)}"
    
    async def explain_code_streaming(self, code: str, output: str = "", error: str = "") -> AsyncGenerator[str, None]:
        """Generate streaming code explanation"""
        try:
            if not self.initialized:
                yield "RAG service not initialized"
                return
            
            # Create query for retrieval
            query = self._create_query(code, output, error)
            yield f"🔍 Analyzing code and searching documentation...\n\n"
            
            # Retrieve relevant documentation
            docs = await self._retrieve_relevant_docs(query)
            yield f"📚 Found {len(docs)} relevant documentation sections\n\n"
            
            # Generate streaming explanation
            async for chunk in self._generate_explanation_streaming(code, output, error, docs):
                yield chunk
                
        except Exception as e:
            logger.error(f"Failed to explain code: {e}")
            yield f"❌ Sorry, I couldn't explain the code due to an error: {str(e)}"
    
    def _create_query(self, code: str, output: str = "", error: str = "") -> str:
        """Create search query from code, output, and error"""
        query_parts = [f"Code: {code}"]
        
        if output:
            query_parts.append(f"Output: {output}")
        
        if error:
            query_parts.append(f"Error: {error}")
        
        return " ".join(query_parts)
    
    async def _retrieve_relevant_docs(self, query: str) -> List[Document]:
        """Retrieve relevant documentation using similarity search"""
        try:
            # Perform similarity search
            docs = self.vectorstore.similarity_search(
                query,
                k=self.max_retrieved_docs
            )
            
            return docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    async def _generate_explanation(self, code: str, output: str, error: str, docs: List[Document]) -> str:
        """Generate explanation using Gemini"""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = self._create_explanation_prompt(code, output, error, context)
            
            # Generate response
            messages = [
                SystemMessage(content="You are an expert programming tutor. Explain code clearly and educationally."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"Error generating explanation: {str(e)}"
    
    async def _generate_explanation_streaming(self, code: str, output: str, error: str, docs: List[Document]) -> AsyncGenerator[str, None]:
        """Generate streaming explanation using Gemini"""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = self._create_explanation_prompt(code, output, error, context)
            
            # Create Gemini model for streaming
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Generate streaming response
            response = model.generate_content(
                prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming explanation: {e}")
            yield f"Error generating explanation: {str(e)}"
    
    def _create_explanation_prompt(self, code: str, output: str, error: str, context: str) -> str:
        """Create explanation prompt for Gemini"""
        prompt_parts = [
            "As an expert programming tutor, explain the following code in a clear, educational way.",
            "",
            "Context from documentation:",
            context,
            "",
            "Code to explain:",
            f"```\n{code}\n```",
        ]
        
        if output:
            prompt_parts.extend([
                "",
                f"Output: {output}"
            ])
        
        if error:
            prompt_parts.extend([
                "",
                f"Error: {error}"
            ])
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "1. Step-by-step explanation of what the code does",
            "2. Explanation of any output or errors",
            "3. Learning points and best practices",
            "4. Suggestions for improvement if applicable",
            "",
            "Use clear, beginner-friendly language with examples when helpful."
        ])
        
        return "\n".join(prompt_parts) 