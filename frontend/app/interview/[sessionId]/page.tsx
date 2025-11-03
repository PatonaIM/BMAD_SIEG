"use client"

import { useParams } from "next/navigation"
import { useEffect, useState, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { useSendMessage } from "@/src/features/interview/hooks/useSendMessage"
import { useInterviewMessages } from "@/src/features/interview/hooks/useInterview"
import { useAudioUpload } from "@/src/features/interview/hooks/useAudioUpload"
import InterviewProgress from "@/src/features/interview/components/InterviewProgress/InterviewProgress"
import { InterviewStateIndicator } from "@/src/features/interview/components/InterviewStateIndicator"
import { InputModeToggle, type InputMode } from "@/src/features/interview/components/InputModeToggle"
import { MicrophonePermissionDialog } from "@/src/features/interview/components/MicrophonePermissionDialog"
import { useAudioCapture } from "@/src/features/interview/hooks/useAudioCapture"
import { useRealtimeInterview } from "@/src/features/interview/hooks/useRealtimeInterview"
import { AudioPlaybackQueue, AudioLevelMonitor } from "@/src/features/interview/utils/audioProcessing"
import { LatencyIndicator } from "@/src/features/interview/components/LatencyIndicator"
import { ConnectionLostBanner } from "@/src/features/interview/components/ConnectionLostBanner"
import { AudioNotSupportedMessage } from "@/src/features/interview/components/AudioNotSupportedMessage"
import { type OrbState } from "@/src/features/interview/components/AIPresenceOrb"
import { useVideoRecorder } from "@/src/features/interview/hooks/useVideoRecorder"
import { videoUploadService } from "@/src/features/interview/services/videoUploadService"
import { useMediaPermissions } from "@/src/hooks/useMediaPermissions"
import { AlertCircle } from "lucide-react"
// Story 2.4: New video layout components
import { VideoGridLayout } from "@/src/features/interview/components/VideoGridLayout"
import { AITile } from "@/src/features/interview/components/AITile"
import { CandidateTile } from "@/src/features/interview/components/CandidateTile"
import { InterviewControls } from "@/src/features/interview/components/InterviewControls"
// Story 2.5: Recording warning toast
import { RecordingWarningToast } from "@/src/features/interview/components/RecordingWarningToast"

export default function InterviewPage() {
  const params = useParams()
  const sessionId = params?.sessionId as string | undefined

  const { 
    messages, 
    isAiTyping, 
    currentQuestion, 
    totalQuestions, 
    setSessionId, 
    setStatus,
    status,
    interviewState,
    setInterviewState,
    inputMode,
    setInputMode,
    currentAudioUrl,
    useRealtimeMode,
    connectionState,
    setConnectionState,
    audioLevel,
    setAudioLevel,
    addMessage,
    // Story 2.4: Caption and self-view state
    currentCaption,
    setCurrentCaption,
    captionsEnabled,
    setCaptionsEnabled,
    showCaption,
    setShowCaption,
    selfViewVisible,
    setSelfViewVisible,
    // Story 2.5: Camera enabled state
    cameraEnabled,
    setCameraEnabled,
  } = useInterviewStore()

  const [showPermissionDialog, setShowPermissionDialog] = useState(false)
  const [isAudioSupported, setIsAudioSupported] = useState(true)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [videoConsentGiven, setVideoConsentGiven] = useState(false)
  const [isVideoRecording, setIsVideoRecording] = useState(false)
  const [uploadedChunks, setUploadedChunks] = useState<number>(0)
  // Story 2.4: Control button states
  const [isMuted, setIsMuted] = useState(false)
  const [isCameraOn, setIsCameraOn] = useState(cameraEnabled)
  const audioPlaybackQueueRef = useRef<AudioPlaybackQueue | null>(null)
  const audioLevelMonitorRef = useRef<AudioLevelMonitor | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioLevelThrottleRef = useRef<number>(0)
  const audioContextRef = useRef<AudioContext | null>(null)
  const audioProcessorRef = useRef<ScriptProcessorNode | null>(null)
  // Story 2.4: Caption timing ref
  const captionTimerRef = useRef<NodeJS.Timeout | null>(null)

  const audioCapture = useAudioCapture()
  
  // Video recording hooks
  const mediaPermissions = useMediaPermissions()
  const videoRecorder = useVideoRecorder()
  const previousChunksCountRef = useRef<number>(0)

  // Map interview state to orb state
  const getOrbState = (): OrbState => {
    switch (interviewState) {
      case 'ai_listening':
        return 'idle'
      case 'ai_speaking':
        return 'speaking'
      case 'candidate_speaking':
        return 'listening'
      case 'processing':
        return 'thinking'
      default:
        return 'idle'
    }
  }

  // Hooks must be declared before conditional logic
  const { mutate: sendMessage, isPending } = useSendMessage({
    sessionId: sessionId || "",
  })

  const { mutate: uploadAudio, isPending: isAudioUploading } = useAudioUpload()

  const { isLoading, isError, error } = useInterviewMessages(sessionId)

  // Initialize Realtime WebSocket connection
  const realtime = useRealtimeInterview(
    sessionId || '',
    {
      onTranscript: (transcript) => {
        addMessage({ 
          role: transcript.role === 'user' ? 'candidate' : 'ai', 
          content: transcript.text 
        })
      },
      onAudioChunk: async (audioData: string) => {
        if (!audioPlaybackQueueRef.current) {
          audioPlaybackQueueRef.current = new AudioPlaybackQueue(24000, {
            onPlaybackStart: () => {
              console.log('🔊 AI audio playback started')
              setInterviewState('ai_speaking')
            },
            onPlaybackEnd: () => {
              console.log('🔇 AI audio playback ended')
              setInterviewState('ai_listening')
            }
          })
        }
        await audioPlaybackQueueRef.current.enqueueBase64(audioData)
      },
      onError: (error: Error) => {
        console.error('Realtime connection error:', error)
        setConnectionState('error')
      },
      onConnected: () => {
        setConnectionState('connected')
      },
      onDisconnected: () => {
        setConnectionState('disconnected')
      },
    }
  )

  // Sync connection state to store
  useEffect(() => {
    setConnectionState(realtime.connectionState)
  }, [realtime.connectionState, setConnectionState])

  // Connect/disconnect realtime WebSocket when mode changes
  useEffect(() => {
    // Don't connect until interview messages are loaded
    if (useRealtimeMode && inputMode === 'voice' && sessionId && !isLoading) {
      realtime.connect()
    } else {
      realtime.disconnect()
    }
    
    return () => {
      realtime.disconnect()
      // Cleanup audio playback queue on unmount
      if (audioPlaybackQueueRef.current) {
        audioPlaybackQueueRef.current.close()
        audioPlaybackQueueRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [useRealtimeMode, inputMode, sessionId, isLoading])
  
  // Check audio support on mount
  useEffect(() => {
    const checkAudioSupport = () => {
      const hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
      const hasMediaRecorder = typeof MediaRecorder !== 'undefined'
      const isSupported = hasMediaDevices && hasMediaRecorder
      setIsAudioSupported(isSupported)
    }
    checkAudioSupport()
  }, [])

  // Auto-request microphone permission when in realtime voice mode
  useEffect(() => {
    const requestMicPermission = async () => {
      if (useRealtimeMode && inputMode === 'voice' && !audioCapture.permissionGranted) {
        console.log('🎤 Requesting microphone permission...')
        const granted = await audioCapture.requestPermission()
        if (!granted) {
          console.error('❌ Microphone permission denied')
          setShowPermissionDialog(true)
        } else {
          console.log('✅ Microphone permission granted')
        }
      }
    }
    requestMicPermission()
  }, [useRealtimeMode, inputMode, audioCapture])

  // Initialize audio level monitor AND start continuous audio streaming for Server VAD
  useEffect(() => {
    if (useRealtimeMode && inputMode === 'voice' && connectionState === 'connected' && audioCapture.permissionGranted) {
      console.log('🎤 Starting continuous audio streaming for Server VAD...')
      
      audioLevelMonitorRef.current = new AudioLevelMonitor()
      
      // Get media stream from audio capture
      const stream = audioCapture.getMediaStream()
      if (stream) {
        mediaStreamRef.current = stream
        
        // Throttle audio level updates to prevent infinite re-renders
        const THROTTLE_MS = 100 // Update max 10 times per second
        
        audioLevelMonitorRef.current.start(stream, (level) => {
          const now = Date.now()
          if (now - audioLevelThrottleRef.current >= THROTTLE_MS) {
            setAudioLevel(level)
            audioLevelThrottleRef.current = now
          }
        })
        
        // Start continuous audio streaming for Server VAD
        // Create audio context with native sample rate
        const audioContext = new AudioContext()
        const source = audioContext.createMediaStreamSource(stream)
        
        // Create script processor for raw PCM data
        const processor = audioContext.createScriptProcessor(8192, 1, 1)
        
        // Calculate resampling ratio (e.g., 48000 Hz → 24000 Hz = 2:1)
        const sourceSampleRate = audioContext.sampleRate
        const targetSampleRate = 24000
        const ratio = sourceSampleRate / targetSampleRate
        
        console.log(`🎤 Audio resampling: ${sourceSampleRate}Hz → ${targetSampleRate}Hz (ratio: ${ratio})`)
        
        let chunkCount = 0
        processor.onaudioprocess = (e) => {
          chunkCount++
          if (chunkCount === 1) {
            console.log('✅ Started sending audio chunks to backend')
          }
          
          const inputData = e.inputBuffer.getChannelData(0) // Float32Array
          
          // Simple downsampling: take every Nth sample
          const outputLength = Math.floor(inputData.length / ratio)
          const resampledData = new Float32Array(outputLength)
          
          for (let i = 0; i < outputLength; i++) {
            const sourceIndex = Math.floor(i * ratio)
            resampledData[i] = inputData[sourceIndex]
          }
          
          // Convert Float32 to Int16 (PCM16)
          const pcm16 = new Int16Array(resampledData.length)
          for (let i = 0; i < resampledData.length; i++) {
            const s = Math.max(-1, Math.min(1, resampledData[i]))
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
          }
          
          // Send to WebSocket (Server VAD will detect when you speak)
          realtime.sendAudioChunk(pcm16.buffer)
          
          if (chunkCount % 100 === 0) {
            console.log(`📤 Sent ${chunkCount} audio chunks (Server VAD active)`)
          }
        }
        
        source.connect(processor)
        processor.connect(audioContext.destination)
        
        // Store references for cleanup
        audioContextRef.current = audioContext
        audioProcessorRef.current = processor
        
        console.log('✅ Continuous audio streaming active - Server VAD will detect when you speak')
      }
      
      return () => {
        console.log('🛑 Stopping continuous audio streaming')
        audioLevelMonitorRef.current?.stop()
        audioLevelMonitorRef.current = null
        
        // Clean up audio streaming
        if (audioProcessorRef.current) {
          audioProcessorRef.current.disconnect()
          audioProcessorRef.current = null
        }
        if (audioContextRef.current) {
          audioContextRef.current.close()
          audioContextRef.current = null
        }
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [useRealtimeMode, inputMode, connectionState, audioCapture.permissionGranted])

  // Track reconnection attempts
  useEffect(() => {
    if (connectionState === 'connecting') {
      setReconnectAttempts(prev => prev + 1)
    } else if (connectionState === 'connected') {
      setReconnectAttempts(0)
    }
  }, [connectionState])

  useEffect(() => {
    if (sessionId) {
      setSessionId(sessionId)
      setStatus("in_progress")
    }
  }, [sessionId, setSessionId, setStatus])

  // Handle audio permission
  useEffect(() => {
    if (inputMode === 'voice' && !audioCapture.permissionGranted) {
      setShowPermissionDialog(true)
    }
  }, [inputMode, audioCapture.permissionGranted])

  // Story 2.5: Sync camera state from store
  useEffect(() => {
    setIsCameraOn(cameraEnabled)
  }, [cameraEnabled])

  // Story 2.5: Request camera permission when page loads (if camera enabled)
  useEffect(() => {
    const requestCameraAccess = async () => {
      if (cameraEnabled && mediaPermissions.cameraStatus === 'idle') {
        console.log('📹 Requesting camera permission...')
        await mediaPermissions.requestCamera()
      }
    }

    requestCameraAccess()
  }, [cameraEnabled, mediaPermissions])

  // Video consent is handled in tech check page, so we don't show the modal here
  // Video recording starts automatically if consent was given and camera is available
  useEffect(() => {
    const startVideoRecording = async () => {
      // Check if consent was given (from tech check) and camera is available
      if (!isVideoRecording && sessionId && mediaPermissions.cameraStatus === 'granted' && mediaPermissions.cameraStream) {
        try {
          // Fetch consent status from backend
          const apiUrl = typeof window !== 'undefined' && (window as any).ENV?.NEXT_PUBLIC_API_BASE_URL 
            ? (window as any).ENV.NEXT_PUBLIC_API_BASE_URL 
            : 'http://localhost:8000'
          
          const response = await fetch(`${apiUrl}/api/v1/interviews/${sessionId}/status`, {
            headers: {
              ...(localStorage.getItem('auth_token') && {
                Authorization: `Bearer ${localStorage.getItem('auth_token')}`
              })
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            
            // Only start recording if consent was given in tech check
            if (data.video_recording_consent) {
              await videoRecorder.startRecording(mediaPermissions.cameraStream)
              setIsVideoRecording(true)
              setVideoConsentGiven(true)
              console.log('✅ Video recording started (consent from tech check)')
            }
          }
        } catch (error) {
          console.error('Failed to check video consent or start recording:', error)
          // Gracefully degrade to audio-only
        }
      }
    }

    startVideoRecording()
  }, [sessionId, isVideoRecording, mediaPermissions.cameraStatus, mediaPermissions.cameraStream, videoRecorder])

  // Upload video chunks as they become available (every 30 seconds)
  useEffect(() => {
    const uploadNewChunks = async () => {
      if (!sessionId || !videoConsentGiven) return

      const currentChunkCount = videoRecorder.videoChunks.length
      const newChunksCount = currentChunkCount - previousChunksCountRef.current

      if (newChunksCount > 0) {
        // Upload each new chunk
        for (let i = previousChunksCountRef.current; i < currentChunkCount; i++) {
          const chunk = videoRecorder.videoChunks[i]
          try {
            await videoUploadService.uploadVideoChunk(
              sessionId,
              chunk,
              i,
              false // Not final chunk yet
            )
            setUploadedChunks(i + 1)
            console.log(`✅ Uploaded video chunk ${i + 1}/${currentChunkCount}`)
          } catch (error) {
            console.error(`Failed to upload video chunk ${i}:`, error)
          }
        }

        previousChunksCountRef.current = currentChunkCount
      }
    }

    uploadNewChunks()
  }, [sessionId, videoConsentGiven, videoRecorder.videoChunks, videoUploadService])

  // Stop video recording when interview ends
  useEffect(() => {
    const stopVideoRecording = async () => {
      if (isVideoRecording && status === 'completed') {
        try {
          await videoRecorder.stopRecording()
          
          // Upload final chunk if any
          if (videoRecorder.videoChunks.length > uploadedChunks && sessionId) {
            const lastChunk = videoRecorder.videoChunks[videoRecorder.videoChunks.length - 1]
            await videoUploadService.uploadVideoChunk(
              sessionId,
              lastChunk,
              videoRecorder.videoChunks.length - 1,
              true // Final chunk
            )
          }
          
          setIsVideoRecording(false)
          console.log('✅ Video recording stopped and uploaded')
        } catch (error) {
          console.error('Failed to stop video recording:', error)
        }
      }
    }

    stopVideoRecording()
  }, [isVideoRecording, status, videoRecorder, sessionId, uploadedChunks, videoUploadService])

  // Story 2.4: Caption sync logic - update caption when AI speaks
  useEffect(() => {
    if (interviewState === 'ai_speaking') {
      // AI is speaking - show caption immediately
      const lastAiMessage = messages
        .filter(m => m.role === 'ai')
        .pop()
      
      if (lastAiMessage) {
        // Clear any existing timer
        if (captionTimerRef.current) {
          clearTimeout(captionTimerRef.current)
          captionTimerRef.current = null
        }
        
        setCurrentCaption(lastAiMessage.content)
        setShowCaption(true)
      }
    } else if (currentCaption && (interviewState === 'ai_listening' || interviewState === 'processing' || interviewState === 'candidate_speaking')) {
      // AI finished speaking - start 3-second fade-out timer
      if (!captionTimerRef.current) {
        captionTimerRef.current = setTimeout(() => {
          setShowCaption(false)
          captionTimerRef.current = null
        }, 3000)
      }
    }
    
    return () => {
      if (captionTimerRef.current) {
        clearTimeout(captionTimerRef.current)
        captionTimerRef.current = null
      }
    }
  }, [interviewState, messages, currentCaption, setCurrentCaption, setShowCaption])

  const handleSendMessage = (messageText: string) => {
    sendMessage(messageText)
  }

  const handleInputModeChange = (mode: InputMode) => {
    setInputMode(mode)
    if (mode === 'voice' && !audioCapture.permissionGranted) {
      setShowPermissionDialog(true)
    }
  }

  const handleAudioRecordStart = async () => {
    if (!audioCapture.permissionGranted) {
      setShowPermissionDialog(true)
      return
    }
    setInterviewState('candidate_speaking')
    
    if (useRealtimeMode) {
      // Realtime mode: Capture raw PCM audio using Web Audio API
      const stream = audioCapture.getMediaStream()
      if (!stream) {
        console.error('No media stream available')
        return
      }
      
      // Create audio context with native sample rate to avoid compatibility issues
      // We'll resample to 24kHz in the processor
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      
      // Create script processor for raw PCM data (deprecated but widely supported)
      // Use larger buffer for better performance: 8192 samples
      const processor = audioContext.createScriptProcessor(8192, 1, 1)
      
      // Calculate resampling ratio (e.g., 48000 Hz → 24000 Hz = 2:1)
      const sourceSampleRate = audioContext.sampleRate
      const targetSampleRate = 24000
      const ratio = sourceSampleRate / targetSampleRate
      
      console.log(`Audio resampling: ${sourceSampleRate}Hz → ${targetSampleRate}Hz (ratio: ${ratio})`)
      
      let chunkCount = 0
      processor.onaudioprocess = (e) => {
        chunkCount++
        if (chunkCount === 1) {
          console.log('✅ First audio chunk received from microphone')
        }
        
        const inputData = e.inputBuffer.getChannelData(0) // Float32Array
        
        // Simple downsampling: take every Nth sample
        const outputLength = Math.floor(inputData.length / ratio)
        const resampledData = new Float32Array(outputLength)
        
        for (let i = 0; i < outputLength; i++) {
          const sourceIndex = Math.floor(i * ratio)
          resampledData[i] = inputData[sourceIndex]
        }
        
        // Convert Float32 to Int16 (PCM16)
        const pcm16 = new Int16Array(resampledData.length)
        for (let i = 0; i < resampledData.length; i++) {
          const s = Math.max(-1, Math.min(1, resampledData[i]))
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
        }
        
        // Send to WebSocket
        if (chunkCount % 10 === 0) {
          console.log(`📤 Sent ${chunkCount} audio chunks (${pcm16.length} samples each)`)
        }
        realtime.sendAudioChunk(pcm16.buffer)
      }
      
      source.connect(processor)
      processor.connect(audioContext.destination)
      
      // Store references for cleanup
      audioContextRef.current = audioContext
      audioProcessorRef.current = processor
      
      setInterviewState('candidate_speaking')
    } else {
      // Legacy mode: Record full audio blob
      await audioCapture.startRecording()
    }
  }

  const handleAudioRecordStop = async () => {
    if (useRealtimeMode) {
      // Clean up Web Audio API resources
      if (audioProcessorRef.current) {
        audioProcessorRef.current.disconnect()
        audioProcessorRef.current = null
      }
      if (audioContextRef.current) {
        await audioContextRef.current.close()
        audioContextRef.current = null
      }
      
      // Commit audio buffer to signal end of input
      realtime.commitAudio()
      setInterviewState('ai_listening')
    } else {
      // Legacy mode: Get recorded blob
      const audioBlob = await audioCapture.stopRecording()
      if (!audioBlob) {
        return
      }
      
      // Legacy mode: Upload audio for transcription
      console.log('✅ Audio blob received:', audioBlob.size, 'bytes')
      console.log('📋 Session info:', { sessionId, messagesLength: messages.length })
      setInterviewState('processing')
      
      uploadAudio(
        { 
          sessionId: sessionId || '', 
          audioBlob,
          messageSequence: messages.length + 1 
        },
        {
          onSuccess: (data) => {
            console.log('🎯 Transcription received:', data.transcription)
            setInterviewState('ai_listening')
          },
          onError: (error) => {
            console.error('❌ Audio upload/transcription failed:', error)
            setInterviewState('ai_listening')
          }
        }
      )
    }
  }

  const handleAudioPlaybackStart = () => {
    setInterviewState('ai_speaking')
  }

  const handleAudioPlaybackEnd = () => {
    setInterviewState('ai_listening')
  }

  const handleAudioPlaybackError = () => {
    // Fall back to text-only mode
    setInterviewState('ai_listening')
  }

  const handlePermissionGranted = async () => {
    // Request permission through the audioCapture hook to sync state
    const granted = await audioCapture.requestPermission()
    if (granted) {
      setShowPermissionDialog(false)
    }
  }

  const handlePermissionDenied = () => {
    setShowPermissionDialog(false)
    setInputMode('text')
  }

  // Story 2.4: Control handlers
  const handleToggleMute = () => {
    setIsMuted(!isMuted)
    // TODO: Actually mute/unmute the microphone stream
    if (mediaStreamRef.current) {
      const audioTracks = mediaStreamRef.current.getAudioTracks()
      audioTracks.forEach(track => {
        track.enabled = isMuted // Toggle enabled state
      })
    }
  }

  const handleToggleCamera = () => {
    const newCameraState = !cameraEnabled
    setCameraEnabled(newCameraState)
    
    // Update local UI state
    setIsCameraOn(newCameraState)
    
    // Stop/start video recording based on camera state
    if (!newCameraState && isVideoRecording) {
      // Turning off - stop recording
      videoRecorder.stopRecording()
      setIsVideoRecording(false)
    } else if (newCameraState && mediaPermissions.cameraStream && videoConsentGiven) {
      // Turning on - start recording
      videoRecorder.startRecording(mediaPermissions.cameraStream)
      setIsVideoRecording(true)
    }
  }

  const handleEndInterview = () => {
    // Show confirmation dialog before ending
    if (window.confirm('Are you sure you want to end the interview?')) {
      setStatus('completed')
      // Navigate to completion page or dashboard
      window.location.href = '/dashboard'
    }
  }

  const handleToggleCaptions = () => {
    setCaptionsEnabled(!captionsEnabled)
  }

  const handleToggleSelfView = () => {
    setSelfViewVisible(!selfViewVisible)
  }

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-destructive/10">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
          </div>
          <h1 className="text-xl font-semibold mb-2">Invalid Interview Session</h1>
          <p className="text-muted-foreground mb-4">
            No session ID provided. Please return to the interview start page.
          </p>
          <Button asChild>
            <a href="/interview/start">Return to Start</a>
          </Button>
        </Card>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
          <p className="text-muted-foreground">Loading interview...</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-md w-full p-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-destructive/10">
              <AlertCircle className="h-6 w-6 text-destructive" />
            </div>
          </div>
          <h1 className="text-xl font-semibold mb-2 text-destructive">Failed to Load Interview</h1>
          <p className="text-muted-foreground mb-4">{error?.message || "Unknown error occurred"}</p>
          <Button variant="outline" asChild>
            <a href="/dashboard">Return to Dashboard</a>
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <>
      {/* Story 2.5: Recording Warning Toast */}
      <RecordingWarningToast 
        sessionId={sessionId || ''}
        isRecording={isVideoRecording && cameraEnabled}
      />

      {/* Connection Lost Banner */}
      <ConnectionLostBanner
        show={useRealtimeMode && inputMode === 'voice' && connectionState === 'disconnected' && reconnectAttempts === 0}
        onRetry={() => realtime.connect()}
        onSwitchToText={() => {
          setInputMode('text')
          realtime.disconnect()
        }}
        attemptCount={reconnectAttempts}
      />

      {/* Audio Not Supported Message */}
      <AudioNotSupportedMessage
        show={!isAudioSupported && inputMode === 'voice'}
        onSwitchToText={() => setInputMode('text')}
      />

      {/* Latency Indicator (realtime mode only) */}
      {useRealtimeMode && inputMode === 'voice' && (
        <LatencyIndicator latency={realtime.latency} />
      )}
      
      {/* Microphone Permission Dialog */}
      <MicrophonePermissionDialog
        show={showPermissionDialog}
        onPermissionGranted={handlePermissionGranted}
        onPermissionDenied={handlePermissionDenied}
      />

      {/* Story 2.4: New Video Grid Layout */}
      <VideoGridLayout audioOnlyMode={!cameraEnabled}>
        {/* AI Tile - Large tile with orb, captions, and state indicators */}
        <AITile
          className="ai-tile"
          orbState={getOrbState()}
          audioLevel={audioLevel}
          caption={currentCaption}
          showCaption={showCaption}
          captionsEnabled={captionsEnabled}
          onToggleCaptions={handleToggleCaptions}
          connectionState={connectionState}
          isRecording={isVideoRecording}
        />

        {/* Candidate Tile - Video preview with toggle (hidden in audio-only mode) */}
        {cameraEnabled && (
          <CandidateTile
            className="candidate-tile"
            videoStream={mediaPermissions.cameraStream}
            isVisible={selfViewVisible}
            onToggleVisibility={handleToggleSelfView}
            isRecording={isVideoRecording}
          />
        )}

        {/* Interview Controls - Mute, camera, end interview */}
        <InterviewControls
          className="interview-controls"
          isMuted={isMuted}
          isCameraOn={isCameraOn}
          onToggleMute={handleToggleMute}
          onToggleCamera={handleToggleCamera}
          onEndInterview={handleEndInterview}
        />
      </VideoGridLayout>

      {/* Progress Bar (overlay on video layout) */}
      {totalQuestions > 0 && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 20 }} className="bg-background/95 backdrop-blur-sm">
          <InterviewProgress current={currentQuestion} total={totalQuestions} />
        </div>
      )}

      {/* Hidden: Interview State Indicator & Mode Toggle (for debugging/accessibility) */}
      <div style={{ position: 'fixed', bottom: 100, left: 16, zIndex: 20 }} className="bg-background/95 backdrop-blur-sm rounded-lg p-2 text-xs">
        <InterviewStateIndicator state={interviewState} />
        <InputModeToggle mode={inputMode} onModeChange={handleInputModeChange} />
      </div>
    </>
  )
}
