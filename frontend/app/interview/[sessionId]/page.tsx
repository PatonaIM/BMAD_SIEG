"use client"

import { useParams } from "next/navigation"
import { useEffect, useState, useRef } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useInterviewStore } from "@/src/features/interview/store/interviewStore"
import { useSendMessage } from "@/src/features/interview/hooks/useSendMessage"
import { useInterviewMessages } from "@/src/features/interview/hooks/useInterview"
import { useAudioUpload } from "@/src/features/interview/hooks/useAudioUpload"
import { InterviewStateIndicator } from "@/src/features/interview/components/InterviewStateIndicator"
import { MicrophonePermissionDialog } from "@/src/features/interview/components/MicrophonePermissionDialog"
import { useAudioCapture } from "@/src/features/interview/hooks/useAudioCapture"
import { useRealtimeInterview } from "@/src/features/interview/hooks/useRealtimeInterview"
import { AudioPlaybackQueue, AudioLevelMonitor } from "@/src/features/interview/utils/audioProcessing"
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
// Story 2.6: Caption sync hook and history modal
import { useCaptionSync } from "@/src/features/interview/hooks/useCaptionSync"
import { CaptionHistory } from "@/src/features/interview/components/CaptionHistory"

export default function InterviewPage() {
  const params = useParams()
  const sessionId = params?.sessionId as string | undefined

  const { 
    messages, 
    setSessionId, 
    setStatus,
    status,
    interviewState,
    setInterviewState,
    useRealtimeMode,
    connectionState,
    setConnectionState,
    audioLevel,
    setAudioLevel,
    addMessage,
    // Story 2.4: Caption and self-view state
    captionsEnabled,
    setCaptionsEnabled,
    selfViewVisible,
    setSelfViewVisible,
    // Story 2.5: Camera always on (for recording), just toggle self-view visibility
    cameraEnabled,
  } = useInterviewStore()

  const [showPermissionDialog, setShowPermissionDialog] = useState(false)
  const [isAudioSupported, setIsAudioSupported] = useState(true)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [videoConsentGiven, setVideoConsentGiven] = useState(false)
  const [isVideoRecording, setIsVideoRecording] = useState(false)
  const [uploadedChunks, setUploadedChunks] = useState<number>(0)
  // Story 2.6: Caption history modal state
  const [showCaptionHistory, setShowCaptionHistory] = useState(false)
  // Track if minimum speaking duration has been met (for Done Speaking button)
  const [canCompleteSpeaking, setCanCompleteSpeaking] = useState(false)
  const audioPlaybackQueueRef = useRef<AudioPlaybackQueue | null>(null)
  const audioLevelMonitorRef = useRef<AudioLevelMonitor | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioLevelThrottleRef = useRef<number>(0)
  const audioContextRef = useRef<AudioContext | null>(null)
  const audioProcessorRef = useRef<ScriptProcessorNode | null>(null)
  // Track when user started speaking (for minimum duration check)
  const speakingStartTimeRef = useRef<number | null>(null)
  // Track when AI last stopped speaking (to prevent false positives from speaker feedback)
  const aiLastStoppedSpeakingRef = useRef<number>(0)

  const audioCapture = useAudioCapture()
  
  // Story 2.6: Caption sync hook
  const captionSync = useCaptionSync({
    interviewState,
    enabled: captionsEnabled
  })
  
  // Video recording hooks
  const mediaPermissions = useMediaPermissions()
  const videoRecorder = useVideoRecorder()
  const previousChunksCountRef = useRef<number>(0)

  // Map interview state to orb state
  const getOrbState = (): OrbState => {
    console.log('🔄 Current interview state:', interviewState)
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
        // Add to messages
        addMessage({ 
          role: transcript.role === 'user' ? 'candidate' : 'ai', 
          content: transcript.text 
        })
        
        // Story 2.6: Pass to caption sync
        captionSync.onTranscript(transcript)
      },
      onAudioChunk: async (audioData: string) => {
        console.log('🎵 Received audio chunk from backend, size:', audioData.length)
        if (!audioPlaybackQueueRef.current) {
          console.log('🎵 Creating new AudioPlaybackQueue with callbacks')
          audioPlaybackQueueRef.current = new AudioPlaybackQueue(24000, {
            onPlaybackStart: () => {
              console.log('🔊 AI audio playback started')
              setInterviewState('ai_speaking')
              // Reset speaking timer when AI starts talking to prevent false "Done Speaking" button
              speakingStartTimeRef.current = null
            },
            onPlaybackEnd: () => {
              console.log('🔇 AI audio playback ended')
              setInterviewState('ai_listening')
              // Reset speaking timer when transitioning to listening
              speakingStartTimeRef.current = null
              // Track when AI stopped speaking to prevent false positives from audio feedback
              aiLastStoppedSpeakingRef.current = Date.now()
            }
          })
        }
        await audioPlaybackQueueRef.current.enqueueBase64(audioData)
        console.log('🎵 Audio chunk enqueued successfully')
      },
      onError: (error: Error) => {
        console.error('Realtime connection error:', error)
        setConnectionState('error')
      },
      onConnected: () => {
        console.log('✅ WebSocket connected - AI will speak first')
        setConnectionState('connected')
        // Set state to 'ai_speaking' since AI always greets first
        // This prevents showing "Your Turn to Speak" prematurely
        setInterviewState('ai_speaking')
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
    if (useRealtimeMode && sessionId && !isLoading) {
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
  }, [useRealtimeMode, sessionId, isLoading])
  
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
      if (useRealtimeMode && !audioCapture.permissionGranted) {
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
  }, [useRealtimeMode, audioCapture])

  // Initialize audio level monitor AND start continuous audio streaming for Server VAD
  useEffect(() => {
    if (useRealtimeMode && connectionState === 'connected' && audioCapture.permissionGranted) {
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
            
            // Detect when user starts speaking based on audio level
            const SPEAKING_THRESHOLD = 0.02
            const AI_COOLDOWN_MS = 1000 // Wait 1 second after AI stops speaking
            const timeSinceAIStopped = now - aiLastStoppedSpeakingRef.current
            
            // CRITICAL: Only auto-detect speaking start when AI is listening (not speaking/processing)
            // This prevents false positives from AI audio bleeding into the microphone
            // ALSO: Only set candidate_speaking if we haven't already set a speaking start time
            // ALSO: Wait for cooldown period after AI stops to prevent speaker feedback false positives
            if (
              level > SPEAKING_THRESHOLD && 
              interviewState === 'ai_listening' && 
              !speakingStartTimeRef.current &&
              timeSinceAIStopped >= AI_COOLDOWN_MS
            ) {
              console.log('🗣️ User started speaking (audio level detected)')
              speakingStartTimeRef.current = Date.now()
              setInterviewState('candidate_speaking')
              setCanCompleteSpeaking(false) // Reset until minimum duration is met
            }
            // NOTE: We do NOT auto-transition back to ai_listening
            // User must click "Done Speaking" button to commit audio and end their turn
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
  }, [useRealtimeMode, connectionState, audioCapture.permissionGranted])

  // Monitor speaking duration to enable "Done Speaking" button after minimum time
  useEffect(() => {
    if (interviewState === 'candidate_speaking' && speakingStartTimeRef.current) {
      const MIN_SPEAKING_DURATION_MS = 1500
      const checkDuration = () => {
        const speakingDuration = Date.now() - (speakingStartTimeRef.current || 0)
        if (speakingDuration >= MIN_SPEAKING_DURATION_MS) {
          setCanCompleteSpeaking(true)
        }
      }
      
      // Check immediately and then every 100ms
      checkDuration()
      const intervalId = setInterval(checkDuration, 100)
      
      return () => clearInterval(intervalId)
    } else {
      // Reset when not speaking
      setCanCompleteSpeaking(false)
    }
  }, [interviewState])

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
    if (!audioCapture.permissionGranted) {
      setShowPermissionDialog(true)
    }
  }, [audioCapture.permissionGranted])

  // Story 2.5: Request camera permission when page loads (camera always on for recording)
  useEffect(() => {
    const requestCameraAccess = async () => {
      if (mediaPermissions.cameraStatus === 'idle') {
        console.log('📹 Requesting camera permission...')
        await mediaPermissions.requestCamera()
      }
    }

    requestCameraAccess()
  }, [mediaPermissions])

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

  // Story 2.6: Old caption sync logic removed - now handled by useCaptionSync hook
  // The caption timing is managed by the useCaptionSync hook which handles:
  // - Filtering user captions (only shows AI)
  // - Text segmentation for long captions
  // - Fade-in/fade-out timing based on AI speaking state
  // - Caption history for accessibility

  const handleSendMessage = (messageText: string) => {
    sendMessage(messageText)
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
    // In voice-only mode, we can't proceed without microphone
    console.error('Microphone permission denied - interview cannot proceed')
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

  const handleDoneSpeaking = () => {
    try {
      console.log('🎯 Done Speaking button clicked, current state:', interviewState)
      
      // Check if user has been speaking for at least 1.5 seconds
      // OpenAI requires at least 100ms of audio, but we need buffer time
      const MIN_SPEAKING_DURATION_MS = 1500
      if (speakingStartTimeRef.current) {
        const speakingDuration = Date.now() - speakingStartTimeRef.current
        if (speakingDuration < MIN_SPEAKING_DURATION_MS) {
          console.warn(`⚠️ Speaking duration too short (${speakingDuration}ms), need at least ${MIN_SPEAKING_DURATION_MS}ms. Ignoring click.`)
          return // Don't commit if too short
        }
      } else {
        console.warn('⚠️ No speaking start time recorded, ignoring Done Speaking click')
        return
      }
      
      // Signal to backend that user is done speaking
      realtime.commitAudio()
      // Transition to processing state (waiting for AI response)
      setInterviewState('processing')
      speakingStartTimeRef.current = null
      setCanCompleteSpeaking(false)
      console.log('✅ User signaled done speaking, state set to processing (waiting for AI response)')
    } catch (error) {
      console.error('❌ Error in handleDoneSpeaking:', error)
    }
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
        show={useRealtimeMode && connectionState === 'disconnected' && reconnectAttempts === 0}
        onRetry={() => realtime.connect()}
        attemptCount={reconnectAttempts}
      />

      {/* Audio Not Supported Message */}
      <AudioNotSupportedMessage
        show={!isAudioSupported}
      />
      
      {/* Microphone Permission Dialog */}
      <MicrophonePermissionDialog
        show={showPermissionDialog}
        onPermissionGranted={handlePermissionGranted}
        onPermissionDenied={handlePermissionDenied}
      />

      {/* Story 2.4: New Video Grid Layout */}
      <VideoGridLayout selfViewVisible={selfViewVisible}>
        {/* AI Tile - Large tile with orb, captions, and state indicators */}
        <AITile
          className="ai-tile"
          orbState={getOrbState()}
          audioLevel={audioLevel}
          caption={captionSync.currentCaption}
          showCaption={captionSync.isVisible}
          captionsEnabled={captionsEnabled}
          onToggleCaptions={handleToggleCaptions}
          connectionState={connectionState}
          isRecording={isVideoRecording}
        />

        {/* Candidate Tile - Only render when self-view is visible */}
        {selfViewVisible && (
          <CandidateTile
            className="candidate-tile"
            videoStream={mediaPermissions.cameraStream}
            isVisible={selfViewVisible}
            onToggleVisibility={handleToggleSelfView}
            isRecording={isVideoRecording}
          />
        )}

        {/* Interview Controls - Show/hide self-view and end interview */}
        <InterviewControls
          className="interview-controls"
          isSelfViewVisible={selfViewVisible}
          onToggleSelfView={handleToggleSelfView}
          onEndInterview={handleEndInterview}
          onDoneSpeaking={handleDoneSpeaking}
          showDoneSpeaking={interviewState === 'candidate_speaking' && canCompleteSpeaking}
        />
      </VideoGridLayout>

      {/* Story 2.6: Caption History Modal */}
      <CaptionHistory
        captions={captionSync.captionHistory}
        open={showCaptionHistory}
        onOpenChange={setShowCaptionHistory}
      />

      {/* Interview State Indicator - Shows whose turn it is to speak */}
      <div style={{ position: 'fixed', bottom: 100, left: 16, zIndex: 20 }} className="bg-background/95 backdrop-blur-sm rounded-lg shadow-lg">
        <InterviewStateIndicator state={interviewState} />
      </div>
    </>
  )
}
