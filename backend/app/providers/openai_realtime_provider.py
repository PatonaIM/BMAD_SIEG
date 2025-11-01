"""OpenAI Realtime API provider for WebSocket-based voice conversation."""

import asyncio
import base64
import json
import time
from typing import Any, Callable
from uuid import UUID

import structlog
import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed, WebSocketException

from app.core.config import settings

logger = structlog.get_logger().bind(provider="openai_realtime")


class OpenAIRealtimeProvider:
    """
    Provider for OpenAI Realtime API WebSocket connections.
    
    Manages bidirectional WebSocket communication with OpenAI's Realtime API
    for speech-to-speech interviews. Handles:
    - WebSocket connection and authentication
    - Audio streaming (PCM16 at 24kHz)
    - Event message handling
    - Connection health monitoring (ping/pong)
    - Automatic reconnection with exponential backoff
    
    Protocol Flow:
    =============
    1. Connect to wss://api.openai.com/v1/realtime
    2. Send session.update with configuration
    3. Stream audio input via conversation.item.create + input_audio_buffer.append
    4. Receive audio output via response.audio.delta events
    5. Handle function calls via response.function_call_arguments.done
    6. Monitor connection with ping/pong
    
    Usage:
    ======
    >>> provider = OpenAIRealtimeProvider()
    >>> 
    >>> # Connect and initialize
    >>> ws = await provider.connect(session_config)
    >>> 
    >>> # Send audio chunk
    >>> await provider.send_audio_chunk(ws, audio_bytes)
    >>> 
    >>> # Receive events
    >>> async for event in provider.receive_events(ws):
    ...     if event["type"] == "response.audio.delta":
    ...         audio_data = base64.b64decode(event["delta"])
    ...         # Play audio
    >>> 
    >>> # Close connection
    >>> await provider.close(ws)
    
    References:
    ===========
    - OpenAI Realtime API Docs: https://platform.openai.com/docs/guides/realtime
    - WebSocket Protocol: https://platform.openai.com/docs/api-reference/realtime
    """
    
    def __init__(self):
        """Initialize OpenAI Realtime Provider."""
        self.api_key = settings.openai_api_key.get_secret_value()
        self.base_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-realtime-preview-2024-10-01"
        self.connection_timeout = 30  # seconds
        self.ping_interval = 20  # seconds
        
        logger.info("openai_realtime_provider_initialized")
    
    async def connect(
        self,
        session_config: dict[str, Any],
        on_event: Callable[[dict], None] | None = None
    ) -> WebSocketClientProtocol:
        """
        Establish WebSocket connection to OpenAI Realtime API.
        
        Connects to the API, authenticates, and initializes the session
        with the provided configuration.
        
        Args:
            session_config: Session configuration dict containing:
                - model: Model name
                - modalities: ["text", "audio"]
                - voice: Voice ID
                - instructions: System prompt
                - tools: Function definitions
                - temperature: Sampling temperature
                - etc.
            on_event: Optional callback for handling events
        
        Returns:
            WebSocket connection object
        
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If connection times out
        """
        url = f"{self.base_url}?model={self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        logger.info(
            "connecting_to_realtime_api",
            url=url,
            model=self.model
        )
        
        try:
            # Establish WebSocket connection
            websocket = await asyncio.wait_for(
                websockets.connect(
                    url,
                    additional_headers=headers,
                    ping_interval=self.ping_interval,
                    ping_timeout=10,
                    close_timeout=10
                ),
                timeout=self.connection_timeout
            )
            
            logger.info(
                "realtime_connection_established",
                connection_id=id(websocket)
            )
            
            # Initialize session with configuration
            await self._initialize_session(websocket, session_config)
            
            return websocket
            
        except asyncio.TimeoutError:
            logger.error("realtime_connection_timeout")
            raise TimeoutError("Connection to OpenAI Realtime API timed out")
        except Exception as e:
            logger.error(
                "realtime_connection_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise ConnectionError(f"Failed to connect to Realtime API: {str(e)}")
    
    async def _initialize_session(
        self,
        websocket: WebSocketClientProtocol,
        session_config: dict[str, Any]
    ) -> None:
        """
        Initialize session with configuration.
        
        Sends session.update event to configure the AI model, voice,
        instructions, tools, and other parameters.
        
        Args:
            websocket: WebSocket connection
            session_config: Session configuration dict
        """
        logger.info(
            "initializing_realtime_session",
            connection_id=id(websocket)
        )
        
        # Send session.update event
        event = {
            "type": "session.update",
            "session": session_config
        }
        
        await websocket.send(json.dumps(event))
        
        # Wait for session.updated confirmation
        response = await websocket.recv()
        response_data = json.loads(response)
        
        if response_data.get("type") == "session.updated":
            logger.info(
                "realtime_session_initialized",
                connection_id=id(websocket)
            )
        else:
            logger.warning(
                "unexpected_session_response",
                response_type=response_data.get("type")
            )
    
    async def send_audio_chunk(
        self,
        websocket: WebSocketClientProtocol,
        audio_data: bytes
    ) -> None:
        """
        Send audio chunk to OpenAI Realtime API.
        
        Encodes PCM16 audio data as base64 and sends via WebSocket.
        
        Args:
            websocket: WebSocket connection
            audio_data: PCM16 audio bytes (24kHz, mono)
        
        Raises:
            ConnectionClosed: If WebSocket connection is closed
        """
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send input_audio_buffer.append event
        event = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        }
        
        try:
            await websocket.send(json.dumps(event))
            
            logger.debug(
                "audio_chunk_sent",
                chunk_size=len(audio_data),
                connection_id=id(websocket)
            )
        except ConnectionClosed:
            logger.error(
                "audio_send_failed_connection_closed",
                connection_id=id(websocket)
            )
            raise
    
    async def commit_audio_buffer(
        self,
        websocket: WebSocketClientProtocol
    ) -> None:
        """
        Commit audio buffer and request response.
        
        Signals end of audio input and requests AI to generate response.
        
        Args:
            websocket: WebSocket connection
        """
        event = {
            "type": "input_audio_buffer.commit"
        }
        
        await websocket.send(json.dumps(event))
        
        logger.debug(
            "audio_buffer_committed",
            connection_id=id(websocket)
        )
    
    async def create_response(
        self,
        websocket: WebSocketClientProtocol
    ) -> None:
        """
        Request AI to create a response.
        
        Triggers the AI to generate and stream a response.
        
        Args:
            websocket: WebSocket connection
        """
        event = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"]
            }
        }
        
        await websocket.send(json.dumps(event))
        
        logger.debug(
            "response_creation_requested",
            connection_id=id(websocket)
        )
    
    async def send_function_call_output(
        self,
        websocket: WebSocketClientProtocol,
        call_id: str,
        output: dict[str, Any]
    ) -> None:
        """
        Send function call result back to OpenAI.
        
        Args:
            websocket: WebSocket connection
            call_id: Function call ID from OpenAI
            output: Function result dict
        """
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(output)
            }
        }
        
        await websocket.send(json.dumps(event))
        
        logger.info(
            "function_call_output_sent",
            call_id=call_id,
            connection_id=id(websocket)
        )
    
    async def receive_events(
        self,
        websocket: WebSocketClientProtocol
    ):
        """
        Receive events from OpenAI Realtime API.
        
        Generator that yields events as they arrive from the WebSocket.
        Handles connection monitoring and error recovery.
        
        Args:
            websocket: WebSocket connection
        
        Yields:
            Dict containing event data
        
        Raises:
            ConnectionClosed: If connection is closed unexpectedly
        """
        try:
            async for message in websocket:
                try:
                    event = json.loads(message)
                    
                    logger.debug(
                        "event_received",
                        event_type=event.get("type"),
                        connection_id=id(websocket)
                    )
                    
                    yield event
                    
                except json.JSONDecodeError as e:
                    logger.error(
                        "invalid_event_json",
                        error=str(e),
                        message=message[:100]
                    )
                    continue
                    
        except ConnectionClosed:
            logger.warning(
                "realtime_connection_closed",
                connection_id=id(websocket)
            )
            raise
    
    async def close(
        self,
        websocket: WebSocketClientProtocol
    ) -> None:
        """
        Close WebSocket connection gracefully.
        
        Args:
            websocket: WebSocket connection to close
        """
        logger.info(
            "closing_realtime_connection",
            connection_id=id(websocket)
        )
        
        try:
            await websocket.close()
            logger.info(
                "realtime_connection_closed",
                connection_id=id(websocket)
            )
        except Exception as e:
            logger.error(
                "error_closing_connection",
                error=str(e),
                connection_id=id(websocket)
            )
    
    async def reconnect_with_backoff(
        self,
        session_config: dict[str, Any],
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ) -> WebSocketClientProtocol:
        """
        Reconnect to OpenAI Realtime API with exponential backoff.
        
        Attempts to reconnect multiple times with increasing delays
        between attempts.
        
        Args:
            session_config: Session configuration dict
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
        
        Returns:
            WebSocket connection object
        
        Raises:
            ConnectionError: If all retry attempts fail
        """
        for attempt in range(max_retries):
            try:
                logger.info(
                    "attempting_reconnect",
                    attempt=attempt + 1,
                    max_retries=max_retries
                )
                
                websocket = await self.connect(session_config)
                
                logger.info(
                    "reconnect_successful",
                    attempt=attempt + 1
                )
                
                return websocket
                
            except (ConnectionError, TimeoutError) as e:
                if attempt < max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    logger.warning(
                        "reconnect_attempt_failed",
                        attempt=attempt + 1,
                        next_retry_delay=delay,
                        error=str(e)
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "reconnect_failed_all_attempts",
                        attempts=max_retries
                    )
                    raise ConnectionError("Failed to reconnect after all attempts")
