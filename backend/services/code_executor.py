import os
import asyncio
import time
import logging
from typing import Dict, Any, AsyncGenerator

# Updated E2B import for modern Code Interpreter SDK
try:
    from e2b_code_interpreter import Sandbox
    E2B_AVAILABLE = True
except ImportError:
    # Fallback if E2B Code Interpreter is not available
    Sandbox = None
    E2B_AVAILABLE = False

from models.requests import ExecutionResult

logger = logging.getLogger(__name__)

class CodeExecutor:
    """Handles secure code execution using E2B Code Interpreter"""
    
    def __init__(self):
        self.e2b_api_key = os.getenv("E2B_API_KEY")
        if not self.e2b_api_key:
            logger.warning("E2B_API_KEY not set. Code execution will use fallback mode.")
        elif not E2B_AVAILABLE:
            logger.warning("E2B Code Interpreter package not available. Code execution will use fallback mode.")
        
        # Supported languages for the unified code interpreter
        self.supported_languages = ["python", "javascript", "bash", "r", "java"]
        
        # Maximum execution time in seconds
        self.max_execution_time = 30
        
    def _is_e2b_enabled(self) -> bool:
        """Check if E2B is properly configured and available"""
        return E2B_AVAILABLE and self.e2b_api_key is not None
        
    async def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code and return complete result"""
        start_time = time.time()
        
        try:
            # Validate language
            if language not in self.supported_languages:
                raise ValueError(f"Unsupported language: {language}. Supported: {self.supported_languages}")
            
            # Validate code
            if not code.strip():
                raise ValueError("Empty code provided")
            
            if self._is_e2b_enabled():
                result = await self._execute_with_e2b(code, language)
            else:
                result = await self._execute_fallback(code, language)
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "execution_time": execution_time,
                "language": language
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Code execution failed: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": execution_time,
                "language": language
            }
    
    async def execute_streaming(self, code: str, language: str = "python") -> AsyncGenerator[Dict[str, Any], None]:
        """Execute code with streaming output"""
        start_time = time.time()
        
        try:
            # Validate inputs
            if language not in self.supported_languages:
                yield {"type": "error", "message": f"Unsupported language: {language}"}
                return
            
            if not code.strip():
                yield {"type": "error", "message": "Empty code provided"}
                return
            
            # Start execution
            yield {"type": "start", "language": language, "timestamp": start_time}
            
            if self._is_e2b_enabled():
                async for chunk in self._execute_streaming_e2b(code, language):
                    yield chunk
            else:
                async for chunk in self._execute_streaming_fallback(code, language):
                    yield chunk
            
            execution_time = time.time() - start_time
            yield {"type": "complete", "execution_time": execution_time}
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Streaming execution failed: {e}")
            yield {
                "type": "error", 
                "message": str(e),
                "execution_time": execution_time
            }
    
    async def _execute_with_e2b(self, code: str, language: str) -> Dict[str, Any]:
        """Execute code using E2B Code Interpreter (modern SDK)"""
        try:
            # Ensure Sandbox is available
            if not self._is_e2b_enabled() or Sandbox is None:
                raise ValueError("E2B Code Interpreter is not available")
                
            # Create sandbox with the modern Code Interpreter
            with Sandbox(api_key=self.e2b_api_key) as sandbox:
                # Execute code using the simplified run_code method
                if language == "python":
                    execution = sandbox.run_code(code, timeout=self.max_execution_time)
                else:
                    # For other languages, wrap them in Python subprocess calls
                    if language == "javascript":
                        # Run JavaScript using Node.js
                        wrapped_code = f'''
import subprocess
import tempfile
import os

js_code = """{code}"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
    f.write(js_code)
    temp_file = f.name

try:
    result = subprocess.run(['node', temp_file], capture_output=True, text=True, timeout={self.max_execution_time})
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    if result.returncode != 0:
        print("EXIT CODE:", result.returncode)
finally:
    os.unlink(temp_file)
'''
                        execution = sandbox.run_code(wrapped_code, timeout=self.max_execution_time)
                    elif language == "bash":
                        # Run bash commands
                        wrapped_code = f'''
import subprocess
result = subprocess.run(['/bin/bash', '-c', """{code}"""], capture_output=True, text=True, timeout={self.max_execution_time})
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
if result.returncode != 0:
    print("EXIT CODE:", result.returncode)
'''
                        execution = sandbox.run_code(wrapped_code, timeout=self.max_execution_time)
                    else:
                        # Fallback to Python for unsupported languages
                        execution = sandbox.run_code(code, timeout=self.max_execution_time)
                
                # Process results from the new SDK
                success = execution.error is None
                output = ""
                error = ""
                
                # Collect stdout logs - logs.stdout is a list of strings
                if hasattr(execution, 'logs') and execution.logs:
                    if hasattr(execution.logs, 'stdout') and execution.logs.stdout:
                        output += "\n".join(execution.logs.stdout)
                    
                    # Collect stderr logs - logs.stderr is a list of strings
                    if hasattr(execution.logs, 'stderr') and execution.logs.stderr:
                        error += "\n".join(execution.logs.stderr)
                
                # Collect results (charts, displays, etc.)
                if hasattr(execution, 'results') and execution.results:
                    for result in execution.results:
                        if hasattr(result, 'text') and result.text:
                            output += result.text + "\n"
                        elif hasattr(result, 'data'):
                            output += str(result.data) + "\n"
                
                # Handle execution errors
                if hasattr(execution, 'error') and execution.error:
                    error += str(execution.error)
                    success = False
                
                return {
                    "success": success,
                    "output": output.strip(),
                    "error": error.strip()
                }
                
        except Exception as e:
            logger.error(f"E2B execution failed: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"E2B execution failed: {str(e)}"
            }
    
    async def _execute_streaming_e2b(self, code: str, language: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute code with E2B Code Interpreter with streaming simulation"""
        try:
            # Execute the code normally (E2B Code Interpreter doesn't have native streaming yet)
            result = await self._execute_with_e2b(code, language)
            
            # Simulate streaming by yielding chunks of output
            if result["output"]:
                lines = result["output"].split('\n')
                for line in lines:
                    if line.strip():
                        yield {"type": "stdout", "content": line}
                        await asyncio.sleep(0.01)  # Small delay for streaming effect
            
            if result["error"]:
                lines = result["error"].split('\n')
                for line in lines:
                    if line.strip():
                        yield {"type": "stderr", "content": line}
                        await asyncio.sleep(0.01)
            
            # Final result
            yield {
                "type": "result",
                "success": result["success"]
            }
            
        except Exception as e:
            logger.error(f"E2B Code Interpreter streaming execution error: {e}")
            yield {"type": "error", "message": f"Code interpreter execution failed: {str(e)}"}
    
    async def _execute_fallback(self, code: str, language: str) -> Dict[str, Any]:
        """Fallback execution without E2B (limited functionality)"""
        logger.warning("Using fallback execution mode - not secure for production!")
        
        if language == "python":
            return await self._execute_python_fallback(code)
        elif language == "javascript":
            return await self._execute_javascript_fallback(code)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Fallback mode doesn't support {language}"
            }
    
    async def _execute_streaming_fallback(self, code: str, language: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Fallback streaming execution"""
        logger.warning("Using fallback streaming execution mode - not secure for production!")
        
        result = await self._execute_fallback(code, language)
        
        # Simulate streaming by yielding chunks
        if result["output"]:
            for line in result["output"].split('\n'):
                if line.strip():
                    yield {"type": "stdout", "content": line}
                    await asyncio.sleep(0.05)
        
        if result["error"]:
            for line in result["error"].split('\n'):
                if line.strip():
                    yield {"type": "stderr", "content": line}
                    await asyncio.sleep(0.05)
        
        yield {
            "type": "result",
            "success": result["success"],
            "exit_code": 0 if result["success"] else 1
        }
    
    async def _execute_python_fallback(self, code: str) -> Dict[str, Any]:
        """Fallback Python execution using exec (NOT SECURE)"""
        try:
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Create restricted globals (basic security attempt)
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'abs': abs,
                    'round': round,
                }
            }
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals)
            
            return {
                "success": True,
                "output": stdout_capture.getvalue(),
                "error": stderr_capture.getvalue()
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def _execute_javascript_fallback(self, code: str) -> Dict[str, Any]:
        """Fallback JavaScript execution using Node.js subprocess"""
        try:
            import subprocess
            import tempfile
            
            # Create temporary file with JavaScript code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute using Node.js
            process = await asyncio.create_subprocess_exec(
                'node', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.max_execution_time
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode() if stdout else "",
                "error": stderr.decode() if stderr else ""
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": "",
                "error": "Execution timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            } 