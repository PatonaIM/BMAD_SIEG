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
import InterviewChat from "@/src/features/interview/components/InterviewChat/InterviewChat"
import ChatInput from "@/src/features/interview/components/ChatInput/ChatInput"
import TypingIndicator from "@/src/features/interview/components/TypingIndicator/TypingIndicator"
import { InterviewStateIndicator } from "@/src/features/interview/components/InterviewStateIndicator"
import { InputModeToggle, type InputMode } from "@/src/features/interview/components/InputModeToggle"
import { PushToTalkButton } from "@/src/features/interview/components/PushToTalkButton"
import { AudioPlayback } from "@/src/features/interview/components/AudioPlayback"
import { MicrophonePermissionDialog } from "@/src/features/interview/components/MicrophonePermissionDialog"
import { useAudioCapture } from "@/src/features/interview/hooks/useAudioCapture"
import { useRealtimeInterview } from "@/src/features/interview/hooks/useRealtimeInterview"
import { AudioPlaybackQueue, AudioLevelMonitor } from "@/src/features/interview/utils/audioProcessing"
import { LatencyIndicator } from "@/src/features/interview/components/LatencyIndicator"
import { ConnectionLostBanner } from "@/src/features/interview/components/ConnectionLostBanner"
import { AudioNotSupportedMessage } from "@/src/features/interview/components/AudioNotSupportedMessage"
import { AlertCircle, WifiOff } from "lucide-react"

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
  } = useInterviewStore()

  const [showPermissionDialog, setShowPermissionDialog] = useState(false)
  const [isAudioSupported, setIsAudioSupported] = useState(true)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const audioPlaybackQueueRef = useRef<AudioPlaybackQueue | null>(null)
  const audioLevelMonitorRef = useRef<AudioLevelMonitor | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioLevelThrottleRef = useRef<number>(0)
  const audioContextRef = useRef<AudioContext | null>(null)
  const audioProcessorRef = useRef<ScriptProcessorNode | null>(null)

  const audioCapture = useAudioCapture()

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
          audioPlaybackQueueRef.current = new AudioPlaybackQueue()
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

  // Initialize audio playback queue
  useEffect(() => {
    if (useRealtimeMode && inputMode === 'voice') {
      audioPlaybackQueueRef.current = new AudioPlaybackQueue()
      return () => {
        audioPlaybackQueueRef.current?.close()
        audioPlaybackQueueRef.current = null
      }
    }
  }, [useRealtimeMode, inputMode])

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

  // Initialize audio level monitor
  useEffect(() => {
    if (useRealtimeMode && inputMode === 'voice' && audioCapture.permissionGranted) {
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
      }
      
      return () => {
        audioLevelMonitorRef.current?.stop()
        audioLevelMonitorRef.current = null
      }
    }
  }, [useRealtimeMode, inputMode, audioCapture.permissionGranted, audioCapture])

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
    <div className="flex flex-col h-screen bg-muted/30 touch-manipulation">
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

      {/* Audio Playback (hidden component) */}
      <AudioPlayback
        audioUrl={currentAudioUrl}
        onPlaybackStart={handleAudioPlaybackStart}
        onPlaybackEnd={handleAudioPlaybackEnd}
        onPlaybackError={handleAudioPlaybackError}
      />

      {/* Progress Bar */}
      {totalQuestions > 0 && (
        <div className="border-b bg-background">
          <InterviewProgress current={currentQuestion} total={totalQuestions} />
        </div>
      )}

      {/* Interview State Indicator & Mode Toggle */}
      <div className="bg-background border-b p-3 md:p-4 space-y-2 md:space-y-3">
        {/* Connection status for realtime mode */}
        {useRealtimeMode && inputMode === 'voice' && (
          <div className="flex items-center gap-2 text-xs">
            {connectionState === 'connecting' && (
              <span className="flex items-center gap-1 text-yellow-600">
                <span className="animate-pulse">●</span> Connecting...
              </span>
            )}
            {connectionState === 'connected' && (
              <span className="flex items-center gap-1 text-green-600">
                <span>●</span> Connected
                {realtime.latency !== null && (
                  <span className="text-muted-foreground ml-2">
                    {realtime.latency}ms
                  </span>
                )}
              </span>
            )}
            {connectionState === 'error' && (
              <span className="flex items-center gap-1 text-red-600">
                <WifiOff className="w-3 h-3" /> Connection Error
              </span>
            )}
          </div>
        )}
        
        <InterviewStateIndicator state={interviewState} />
        <InputModeToggle mode={inputMode} onModeChange={handleInputModeChange} />
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <InterviewChat messages={messages} isTyping={isAiTyping} />

        {isAiTyping && (
          <div className="px-4">
            <TypingIndicator isVisible={isAiTyping} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-background p-3 md:p-4">
        {inputMode === 'voice' ? (
          <div className="flex flex-col items-center gap-3">
            {/* Audio level indicator for realtime mode */}
            {useRealtimeMode && audioLevel > 0 && (
              <div className="w-full max-w-md">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Mic Level:</span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 transition-all duration-100"
                      style={{ width: `${audioLevel * 100}%` }}
                    />
                  </div>
                  <span>{Math.round(audioLevel * 100)}%</span>
                </div>
              </div>
            )}
            
            <div className="flex justify-center min-h-20 items-center w-full">
              <PushToTalkButton
                state={audioCapture.state}
                error={audioCapture.error}
                onMouseDown={handleAudioRecordStart}
                onMouseUp={handleAudioRecordStop}
                onTouchStart={handleAudioRecordStart}
                onTouchEnd={handleAudioRecordStop}
                disabled={isPending || isAudioUploading || isAiTyping || interviewState === 'ai_speaking' || (useRealtimeMode && connectionState !== 'connected')}
                className="w-full max-w-md"
              />
            </div>
          </div>
        ) : (
          <ChatInput
            onSubmit={handleSendMessage}
            disabled={isPending || isAiTyping}
            placeholder="Type your response..."
          />
        )}
      </div>
    </div>
  )
}
