import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
import json

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for multiple clients"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_tasks: Dict[str, List[asyncio.Task]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_tasks[client_id] = []
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            # Cancel any running tasks for this client
            if client_id in self.client_tasks:
                for task in self.client_tasks[client_id]:
                    if not task.done():
                        task.cancel()
                del self.client_tasks[client_id]
            
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_text = json.dumps(message)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def disconnect_all(self):
        """Disconnect all clients"""
        for client_id in list(self.active_connections.keys()):
            self.disconnect(client_id)
        logger.info("All clients disconnected")
    
    def get_client_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def is_client_connected(self, client_id: str) -> bool:
        """Check if a specific client is connected"""
        return client_id in self.active_connections
    
    async def add_client_task(self, client_id: str, task: asyncio.Task):
        """Add a task for a specific client"""
        if client_id in self.client_tasks:
            self.client_tasks[client_id].append(task) 