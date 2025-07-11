import os
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

from services.code_executor import CodeExecutor
from services.rag_service import RAGService
from services.websocket_manager import WebSocketManager
from models.requests import ExecuteCodeRequest, ExplainCodeRequest

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Code Tutor",
    description="Interactive code interpreter with RAG-powered explanations",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
websocket_manager = WebSocketManager()
code_executor = CodeExecutor()
rag_service = RAGService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await rag_service.initialize()
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await websocket_manager.disconnect_all()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Smart Code Tutor API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "rag": rag_service.is_initialized(),
            "executor": True,
            "websocket": True
        }
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for code execution and explanations"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "execute_code":
                await handle_code_execution(websocket, client_id, data)
            elif action == "explain_code":
                await handle_code_explanation(websocket, client_id, data)
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        await websocket.send_json({
            "type": "error", 
            "message": "Internal server error"
        })

async def handle_code_execution(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """Handle code execution request"""
    try:
        code = data.get("code", "")
        language = data.get("language", "python")
        
        if not code.strip():
            await websocket.send_json({
                "type": "error",
                "message": "No code provided"
            })
            return
        
        # Send execution start status
        await websocket.send_json({
            "type": "execution_start",
            "language": language
        })
        
        # Execute code and stream results
        async for result in code_executor.execute_streaming(code, language):
            await websocket.send_json({
                "type": "execution_output",
                "data": result
            })
        
        # Send execution complete status
        await websocket.send_json({
            "type": "execution_complete"
        })
        
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Execution failed: {str(e)}"
        })

async def handle_code_explanation(websocket: WebSocket, client_id: str, data: Dict[str, Any]):
    """Handle code explanation request"""
    try:
        code = data.get("code", "")
        output = data.get("output", "")
        error = data.get("error", "")
        
        if not code.strip():
            await websocket.send_json({
                "type": "error",
                "message": "No code provided for explanation"
            })
            return
        
        # Send explanation start status
        await websocket.send_json({
            "type": "explanation_start"
        })
        
        # Generate explanation and stream results
        async for explanation_chunk in rag_service.explain_code_streaming(code, output, error):
            await websocket.send_json({
                "type": "explanation_chunk",
                "data": explanation_chunk
            })
        
        # Send explanation complete status
        await websocket.send_json({
            "type": "explanation_complete"
        })
        
    except Exception as e:
        logger.error(f"Code explanation error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Explanation failed: {str(e)}"
        })

# Additional REST endpoints for testing
@app.post("/api/execute")
async def execute_code_rest(request: ExecuteCodeRequest):
    """REST endpoint for code execution (non-streaming)"""
    try:
        result = await code_executor.execute(request.code, request.language)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain")
async def explain_code_rest(request: ExplainCodeRequest):
    """REST endpoint for code explanation (non-streaming)"""
    try:
        explanation = await rag_service.explain_code(request.code, request.output, request.error)
        return JSONResponse(content={"explanation": explanation})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 