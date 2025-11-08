"""Realtime WebSocket API endpoints for voice interviews."""

import asyncio
import base64
import json
import time
from datetime import datetime
from typing import Dict
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.providers.openai_provider import OpenAIProvider
from app.providers.openai_realtime_provider import OpenAIRealtimeProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.services.realtime_interview_service import RealtimeInterviewService

logger = structlog.get_logger().bind(module="realtime_api")

router = APIRouter(prefix="/interviews", tags=["realtime", "websocket"])


# Track active connections to enforce rate limiting
active_connections: Dict[UUID, WebSocket] = {}


async def verify_interview_access(
    interview_id: UUID,
    current_user: Candidate,
    db: AsyncSession
) -> Interview:
    """
    Verify user has access to interview.
    
    Args:
        interview_id: Interview UUID
        current_user: Authenticated candidate
        db: Database session
    
    Returns:
        Interview object
    
    Raises:
        HTTPException: If interview not found or access denied
    """
    interview_repo = InterviewRepository(db)
    interview = await interview_repo.get_by_id(interview_id)
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview"
        )
    
    if interview.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview already completed"
        )
    
    if interview.status == "abandoned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview was abandoned"
        )
    
    return interview


@router.websocket("/{interview_id}/realtime/connect")
async def realtime_connect(
    websocket: WebSocket,
    interview_id: UUID,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for OpenAI Realtime API voice interviews.
    
    Establishes bidirectional WebSocket connection for real-time voice
    conversation between candidate and AI interviewer. Handles:
    - Audio streaming (PCM16 at 24kHz)
    - Transcript synchronization
    - Function call processing (answer evaluation)
    - Connection lifecycle management
    - Error handling and reconnection
    
    Protocol:
    =========
    1. Client connects with JWT token in query params (?token=...)
    2. Server validates access and checks rate limits
    3. Server connects to OpenAI Realtime API
    4. Server proxies messages between client and OpenAI
    5. Server stores transcripts and handles function calls
    6. Connection closes when interview completes or client disconnects
    
    Message Format (Client → Server):
    =================================
    {
        "type": "audio_chunk",
        "audio": "base64_encoded_pcm16_data",
        "timestamp": 1699999999
    }
    
    Message Format (Server → Client):
    =================================
    {
        "type": "ai_audio_chunk",
        "audio": "base64_encoded_pcm16_data",
        "transcript": "partial transcript...",
        "is_final": false
    }
    
    Or:
    {
        "type": "transcript",
        "role": "assistant",
        "text": "Complete AI response",
        "message_id": "uuid"
    }
    
    Args:
        websocket: WebSocket connection
        interview_id: Interview UUID
        db: Database session
    
    Raises:
        WebSocketDisconnect: When client disconnects
    """
    client_connected = False
    openai_ws = None
    correlation_id = f"realtime_{interview_id}_{int(time.time())}"
    
    logger.info(
        "realtime_connection_request",
        interview_id=str(interview_id),
        correlation_id=correlation_id
    )
    
    try:
        # Accept WebSocket connection
        await websocket.accept()
        client_connected = True
        
        logger.info(
            "websocket_accepted",
            interview_id=str(interview_id),
            correlation_id=correlation_id
        )
        
        # Authenticate user with JWT token from query params
        from app.core.security import verify_token
        from app.repositories.candidate import CandidateRepository
        from jose import JWTError
        
        try:
            user_id = verify_token(token)
            candidate_repo = CandidateRepository(db)
            current_user = await candidate_repo.get_by_id(user_id)
            
            if not current_user:
                logger.warning(
                    "authentication_failed_user_not_found",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id
                )
                await websocket.send_json({
                    "type": "error",
                    "error": "AUTHENTICATION_FAILED",
                    "message": "Invalid authentication credentials"
                })
                await websocket.close(code=1008)  # Policy violation
                return
        except (JWTError, Exception) as e:
            logger.warning(
                "authentication_failed",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                error=str(e)
            )
            await websocket.send_json({
                "type": "error",
                "error": "AUTHENTICATION_FAILED",
                "message": "Invalid or expired token"
            })
            await websocket.close(code=1008)  # Policy violation
            return
        
        # Rate limiting: Check if interview already has active connection
        if interview_id in active_connections:
            logger.warning(
                "closing_existing_connection",
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
            # Close the existing connection to allow new one
            try:
                old_ws = active_connections[interview_id]
                await old_ws.close(code=1000, reason="New connection established")
            except Exception as e:
                logger.warning(
                    "failed_to_close_old_connection",
                    error=str(e),
                    correlation_id=correlation_id
                )
            finally:
                # Remove old connection from tracking
                del active_connections[interview_id]
        
        # Register active connection
        active_connections[interview_id] = websocket
        
        # Verify interview access (user must own the interview)
        interview_repo = InterviewRepository(db)
        interview = await interview_repo.get_by_id(interview_id)
        
        if not interview:
            await websocket.send_json({
                "type": "error",
                "error": "INTERVIEW_NOT_FOUND",
                "message": "Interview not found"
            })
            await websocket.close(code=1008)
            return
        
        # Verify interview belongs to authenticated user
        if interview.candidate_id != current_user.id:
            logger.warning(
                "access_denied_not_owner",
                interview_id=str(interview_id),
                user_id=str(current_user.id),
                correlation_id=correlation_id
            )
            await websocket.send_json({
                "type": "error",
                "error": "ACCESS_DENIED",
                "message": "You do not have access to this interview"
            })
            await websocket.close(code=1008)
            return
        
        if interview.status not in ["scheduled", "in_progress"]:
            await websocket.send_json({
                "type": "error",
                "error": "INTERVIEW_NOT_ACTIVE",
                "message": f"Interview status is {interview.status}"
            })
            await websocket.close(code=1008)
            return
        
        # Update interview status to in_progress if needed
        if interview.status == "scheduled":
            await interview_repo.update_status(interview_id, "in_progress")
            # Set started_at timestamp for duration calculation
            interview.started_at = datetime.utcnow()
            await interview_repo.update(interview)
            await db.commit()
            
            logger.info(
                "interview_started",
                interview_id=str(interview_id),
                started_at=interview.started_at.isoformat(),
                correlation_id=correlation_id
            )
        
        # Initialize services
        session_repo = InterviewSessionRepository(db)
        message_repo = InterviewMessageRepository(db)
        ai_provider = OpenAIProvider()
        
        realtime_service = RealtimeInterviewService(
            ai_provider=ai_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )
        
        # Get interview session
        session = await session_repo.get_by_interview_id(interview_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "error": "SESSION_NOT_FOUND",
                "message": "Interview session not found"
            })
            await websocket.close(code=1011)
            return
        
        # Initialize OpenAI Realtime API session
        session_config = await realtime_service.initialize_session(
            interview_id=interview_id,
            session_id=session.id
        )
        
        # Connect to OpenAI Realtime API
        openai_provider = OpenAIRealtimeProvider()
        
        try:
            logger.info(
                "attempting_openai_connection",
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
            
            openai_ws = await asyncio.wait_for(
                openai_provider.connect(session_config),
                timeout=45.0  # 45 second timeout for OpenAI connection
            )
            
            logger.info(
                "realtime_session_established",
                interview_id=str(interview_id),
                session_id=str(session.id),
                correlation_id=correlation_id
            )
        except asyncio.TimeoutError:
            logger.error(
                "openai_connection_timeout",
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
            await websocket.send_json({
                "type": "error",
                "error": "CONNECTION_TIMEOUT",
                "message": "Failed to connect to OpenAI Realtime API - connection timed out"
            })
            await websocket.close(code=1011)
            return
        except (ConnectionError, TimeoutError) as e:
            logger.error(
                "openai_connection_failed",
                interview_id=str(interview_id),
                error=str(e),
                correlation_id=correlation_id
            )
            await websocket.send_json({
                "type": "error",
                "error": "CONNECTION_FAILED",
                "message": f"Failed to connect to OpenAI Realtime API: {str(e)}"
            })
            await websocket.close(code=1011)
            return
        except Exception as e:
            logger.error(
                "openai_connection_unexpected_error",
                interview_id=str(interview_id),
                error=str(e),
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )
            await websocket.send_json({
                "type": "error",
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while connecting to AI service"
            })
            await websocket.close(code=1011)
            return
        
        # Send connection success message to client
        await websocket.send_json({
            "type": "connected",
            "session_id": str(session.id),
            "interview_id": str(interview_id),
            "message": "Realtime connection established"
        })
        
        # Trigger AI to speak first with greeting
        # This initiates the interview conversation
        try:
            await openai_provider.create_response(openai_ws)
            
            logger.info(
                "initial_ai_greeting_triggered",
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
        except Exception as e:
            logger.error(
                "failed_to_trigger_initial_greeting",
                interview_id=str(interview_id),
                error=str(e),
                error_type=type(e).__name__,
                correlation_id=correlation_id
            )
        
        # Create bidirectional message forwarding tasks
        client_to_openai_task = asyncio.create_task(
            forward_client_to_openai(
                client_ws=websocket,
                openai_ws=openai_ws,
                openai_provider=openai_provider,
                correlation_id=correlation_id
            )
        )
        
        openai_to_client_task = asyncio.create_task(
            forward_openai_to_client(
                client_ws=websocket,
                openai_ws=openai_ws,
                openai_provider=openai_provider,
                realtime_service=realtime_service,
                interview_id=interview_id,
                session_id=session.id,
                correlation_id=correlation_id
            )
        )
        
        # Wait for either task to complete (usually due to disconnect)
        done, pending = await asyncio.wait(
            [client_to_openai_task, openai_to_client_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info(
            "realtime_session_ended",
            interview_id=str(interview_id),
            correlation_id=correlation_id
        )
        
    except WebSocketDisconnect:
        logger.info(
            "client_disconnected",
            interview_id=str(interview_id),
            correlation_id=correlation_id
        )
        
    except Exception as e:
        logger.error(
            "realtime_connection_error",
            interview_id=str(interview_id),
            error=str(e),
            error_type=type(e).__name__,
            correlation_id=correlation_id
        )
        
        if client_connected:
            try:
                await websocket.send_json({
                    "type": "error",
                    "error": "INTERNAL_ERROR",
                    "message": "An error occurred during the interview session"
                })
            except Exception:
                pass
        
    finally:
        # CRITICAL: Commit any pending transcripts before cleanup
        # This is a safety net to catch any uncommitted transactions
        # Check if there are actually pending changes before committing
        try:
            if db.in_transaction():
                logger.info(
                    "committing_pending_transcripts_on_cleanup",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id
                )
                await db.commit()
                logger.info(
                    "committed_pending_transcripts_on_cleanup",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id
                )
            else:
                logger.debug(
                    "no_pending_transactions_on_cleanup",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id
                )
        except Exception as commit_error:
            logger.error(
                "failed_to_commit_on_cleanup",
                error=str(commit_error),
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
            try:
                await db.rollback()
            except Exception:
                pass
        
        # Cleanup
        if interview_id in active_connections:
            del active_connections[interview_id]
        
        if openai_ws:
            try:
                await openai_provider.close(openai_ws)
            except Exception:
                pass
        
        if client_connected:
            try:
                await websocket.close()
            except Exception:
                pass
        
        logger.info(
            "realtime_connection_cleaned_up",
            interview_id=str(interview_id),
            correlation_id=correlation_id
        )


async def forward_client_to_openai(
    client_ws: WebSocket,
    openai_ws,
    openai_provider: OpenAIRealtimeProvider,
    correlation_id: str
):
    """
    Forward messages from client to OpenAI Realtime API.
    
    Args:
        client_ws: Client WebSocket connection
        openai_ws: OpenAI WebSocket connection
        openai_provider: OpenAI Realtime provider
        correlation_id: Correlation ID for logging
    """
    try:
        while True:
            # Receive message from client
            data = await client_ws.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "audio_chunk":
                # Forward audio chunk to OpenAI
                audio_base64 = data.get("audio")
                if audio_base64:
                    # Decode from base64
                    audio_data = base64.b64decode(audio_base64)
                    
                    # Send to OpenAI
                    await openai_provider.send_audio_chunk(openai_ws, audio_data)
                    
                    logger.debug(
                        "audio_chunk_forwarded_to_openai",
                        chunk_size=len(audio_data),
                        correlation_id=correlation_id
                    )
            
            elif message_type == "audio_commit":
                # Commit audio buffer
                await openai_provider.commit_audio_buffer(openai_ws)
                
                logger.debug(
                    "audio_buffer_committed",
                    correlation_id=correlation_id
                )
                
                # Request AI to generate response
                await openai_provider.create_response(openai_ws)
                
                logger.debug(
                    "ai_response_requested",
                    correlation_id=correlation_id
                )
            
            elif message_type == "ping":
                # Respond with pong
                await client_ws.send_json({"type": "pong"})
            
            else:
                logger.warning(
                    "unknown_message_type_from_client",
                    message_type=message_type,
                    correlation_id=correlation_id
                )
                
    except WebSocketDisconnect:
        logger.info(
            "client_disconnected_during_forward",
            correlation_id=correlation_id
        )
    except Exception as e:
        logger.error(
            "error_forwarding_client_to_openai",
            error=str(e),
            correlation_id=correlation_id
        )
        raise


async def forward_openai_to_client(
    client_ws: WebSocket,
    openai_ws,
    openai_provider: OpenAIRealtimeProvider,
    realtime_service: RealtimeInterviewService,
    interview_id: UUID,
    session_id: UUID,
    correlation_id: str
):
    """
    Forward events from OpenAI to client and handle server-side processing.
    
    Args:
        client_ws: Client WebSocket connection
        openai_ws: OpenAI WebSocket connection
        openai_provider: OpenAI Realtime provider
        realtime_service: Realtime interview service
        interview_id: Interview UUID
        session_id: Session UUID
        correlation_id: Correlation ID for logging
    """
    try:
        async for event in openai_provider.receive_events(openai_ws):
            event_type = event.get("type")
            
            # Handle different event types
            if event_type == "response.audio.delta":
                # Forward audio chunk to client
                audio_base64 = event.get("delta")
                if audio_base64:
                    await client_ws.send_json({
                        "type": "ai_audio_chunk",
                        "audio": audio_base64,
                        "is_final": False
                    })
            
            elif event_type == "response.audio_transcript.delta":
                # Forward partial transcript to client
                transcript_delta = event.get("delta")
                if transcript_delta:
                    await client_ws.send_json({
                        "type": "transcript_delta",
                        "role": "assistant",
                        "text": transcript_delta,
                        "is_final": False
                    })
            
            elif event_type == "response.audio_transcript.done":
                # Store complete AI transcript
                transcript = event.get("transcript")
                if transcript:
                    message_id = await realtime_service.store_transcript(
                        interview_id=interview_id,
                        session_id=session_id,
                        message_type="ai_question",
                        transcript=transcript,
                        audio_metadata={
                            "event_type": event_type,
                            "timestamp": time.time()
                        }
                    )
                    
                    # CRITICAL: Commit immediately to persist transcript
                    # This ensures data safety if connection drops unexpectedly
                    try:
                        await realtime_service.commit_transaction()
                        logger.debug(
                            "ai_transcript_committed",
                            message_id=str(message_id),
                            correlation_id=correlation_id
                        )
                    except Exception as commit_error:
                        logger.error(
                            "failed_to_commit_ai_transcript",
                            error=str(commit_error),
                            message_id=str(message_id),
                            correlation_id=correlation_id
                        )
                    
                    await client_ws.send_json({
                        "type": "transcript",
                        "role": "assistant",
                        "text": transcript,
                        "message_id": str(message_id),
                        "is_final": True
                    })
            
            elif event_type == "conversation.item.input_audio_transcription.completed":
                # Store candidate transcript
                transcript = event.get("transcript")
                if transcript:
                    message_id = await realtime_service.store_transcript(
                        interview_id=interview_id,
                        session_id=session_id,
                        message_type="candidate_response",
                        transcript=transcript,
                        audio_metadata={
                            "event_type": event_type,
                            "timestamp": time.time()
                        }
                    )
                    
                    # CRITICAL: Commit immediately to persist transcript
                    # This ensures data safety if connection drops unexpectedly
                    try:
                        await realtime_service.commit_transaction()
                        logger.debug(
                            "candidate_transcript_committed",
                            message_id=str(message_id),
                            correlation_id=correlation_id
                        )
                    except Exception as commit_error:
                        logger.error(
                            "failed_to_commit_candidate_transcript",
                            error=str(commit_error),
                            message_id=str(message_id),
                            correlation_id=correlation_id
                        )
                    
                    await client_ws.send_json({
                        "type": "transcript",
                        "role": "user",
                        "text": transcript,
                        "message_id": str(message_id),
                        "is_final": True
                    })
            
            elif event_type == "response.function_call_arguments.done":
                # Handle function call
                function_name = event.get("name")
                arguments_str = event.get("arguments")
                call_id = event.get("call_id")
                
                if function_name and arguments_str:
                    try:
                        arguments = json.loads(arguments_str)
                        
                        # Process function call
                        result = await realtime_service.handle_function_call(
                            function_name=function_name,
                            arguments=arguments,
                            session_id=session_id,
                            interview_id=interview_id
                        )
                        
                        # Send result back to OpenAI
                        await openai_provider.send_function_call_output(
                            openai_ws,
                            call_id,
                            result
                        )
                        
                        logger.info(
                            "function_call_processed",
                            function_name=function_name,
                            call_id=call_id,
                            correlation_id=correlation_id
                        )
                        
                    except json.JSONDecodeError as e:
                        logger.error(
                            "function_arguments_json_error",
                            error=str(e),
                            arguments=arguments_str,
                            correlation_id=correlation_id
                        )
            
            elif event_type == "error":
                # Forward error to client
                error_data = event.get("error", {})
                await client_ws.send_json({
                    "type": "error",
                    "error": error_data.get("code", "UNKNOWN_ERROR"),
                    "message": error_data.get("message", "An error occurred")
                })
                
                logger.error(
                    "openai_error_event",
                    error=error_data,
                    correlation_id=correlation_id
                )
            
            else:
                # Log other events for debugging
                logger.debug(
                    "openai_event",
                    event_type=event_type,
                    correlation_id=correlation_id
                )
                
    except Exception as e:
        logger.error(
            "error_forwarding_openai_to_client",
            error=str(e),
            error_type=type(e).__name__,
            correlation_id=correlation_id
        )
        raise
