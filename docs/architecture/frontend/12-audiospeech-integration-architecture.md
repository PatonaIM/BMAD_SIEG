# 12. Audio/Speech Integration Architecture

## 12.1 Speech Service Provider Strategy

**Primary Provider (MVP): OpenAI Whisper + TTS**

The architecture uses OpenAI for speech processing to simplify vendor management and reduce operational complexity during the bootstrap phase.

**Design Principles:**
- **Provider Abstraction**: Speech services accessed through abstraction layer
- **Flexible Architecture**: Easy migration to Azure Speech Services or GCP alternatives
- **Backend Processing**: All audio processing on server for security and auditability
- **Cost Optimization**: Single vendor billing, batch processing reduces overhead

**Future Migration Path:**
- Post-MVP: Evaluate Azure Speech Services for real-time streaming (<1s latency)
- Post-MVP: Consider GCP Speech-to-Text for specific regional requirements
- Architecture supports provider switching without frontend changes

## 12.2 Speech-to-Text Integration (OpenAI Whisper)

## 12.2 Speech-to-Text Integration (OpenAI Whisper)

```typescript
// src/services/audio/speechService.ts
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY, // Server-side only
});

export class SpeechService {
  /**
   * Transcribe audio file using OpenAI Whisper
   * Processing time: 2-3 seconds typical
   */
  async transcribeAudio(audioFile: File): Promise<TranscriptionResult> {
    try {
      const transcription = await openai.audio.transcriptions.create({
        file: audioFile,
        model: "whisper-1",
        language: "en", // Can be omitted for auto-detection
        response_format: "verbose_json", // Includes timestamps
        temperature: 0.0, // Deterministic output
      });

      return {
        text: transcription.text,
        duration: transcription.duration,
        language: transcription.language,
        segments: transcription.segments, // Word-level timestamps
      };
    } catch (error) {
      throw new Error(`Whisper transcription failed: ${error.message}`);
    }
  }

  /**
   * Transcribe with confidence scores and metadata
   */
  async transcribeWithMetadata(
    audioFile: File,
    interviewId: string
  ): Promise<DetailedTranscription> {
    const startTime = Date.now();
    
    const result = await this.transcribeAudio(audioFile);
    
    const processingTime = Date.now() - startTime;
    
    // Store metadata for integrity monitoring
    return {
      ...result,
      metadata: {
        processingTime,
        audioSize: audioFile.size,
        timestamp: new Date().toISOString(),
        interviewId,
      },
    };
  }
}

export const speechService = new SpeechService();
```

**Backend API Endpoint:**

```python
# backend/api/interviews.py
from fastapi import APIRouter, UploadFile, HTTPException
from openai import OpenAI
import tempfile
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/api/v1/interviews/{interview_id}/audio")
async def process_audio(interview_id: str, audio_file: UploadFile):
    """
    Process candidate audio and return transcription
    Expected latency: 2-3 seconds
    """
    # Validate audio file
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(400, "Invalid audio file format")
    
    # Save temporarily for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        content = await audio_file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Call OpenAI Whisper
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                language="en"
            )
        
        # Store transcription in database
        await store_interview_message(
            interview_id=interview_id,
            role="candidate",
            content=transcription.text,
            audio_metadata={
                "duration": transcription.duration,
                "file_size": len(content),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "transcription": transcription.text,
            "duration": transcription.duration,
            "processing_time": time.time() - start_time
        }
    
    finally:
        # Cleanup temp file
        os.unlink(tmp_path)
```

## 12.3 Text-to-Speech Integration (OpenAI TTS)

## 12.3 Text-to-Speech Integration (OpenAI TTS)

```typescript
// src/services/audio/ttsService.ts
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export class TextToSpeechService {
  /**
   * Generate speech from text using OpenAI TTS
   * Voice options: alloy, echo, fable, onyx, nova, shimmer
   */
  async generateSpeech(
    text: string,
    voice: 'alloy' | 'echo' | 'fable' | 'onyx' | 'nova' | 'shimmer' = 'nova'
  ): Promise<Buffer> {
    try {
      const mp3 = await openai.audio.speech.create({
        model: "tts-1", // Use tts-1-hd for higher quality
        voice: voice,
        input: text,
        speed: 0.95, // Slightly slower for clarity
      });

      const buffer = Buffer.from(await mp3.arrayBuffer());
      return buffer;
    } catch (error) {
      throw new Error(`TTS generation failed: ${error.message}`);
    }
  }

  /**
   * Generate speech with caching for common phrases
   */
  async generateWithCache(text: string, interviewId: string): Promise<string> {
    // Check cache first
    const cached = await this.checkCache(text);
    if (cached) return cached;

    // Generate new audio
    const audioBuffer = await this.generateSpeech(text);
    
    // Save to storage and return URL
    const audioUrl = await this.saveAudio(audioBuffer, interviewId);
    
    // Cache for reuse
    await this.cacheAudio(text, audioUrl);
    
    return audioUrl;
  }
}

export const ttsService = new TextToSpeechService();
```

**Backend Implementation:**

```python
# backend/api/tts.py
from openai import OpenAI
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

router = APIRouter()
client = OpenAI()

@router.post("/api/v1/interviews/{interview_id}/tts")
async def generate_speech(interview_id: str, text: str, voice: str = "nova"):
    """
    Generate speech audio from AI question text
    Expected latency: 1-2 seconds
    """
    try:
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1-hd for higher quality
            voice=voice,
            input=text,
            speed=0.95
        )
        
        # Stream audio back to frontend
        audio_stream = io.BytesIO(response.content)
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=speech_{interview_id}.mp3"
            }
        )
    
    except Exception as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")
```

## 12.4 Frontend Audio Capture

```typescript
// src/services/audio/audioCapture.ts
export class AudioCaptureService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;

  /**
   * Request microphone access and initialize MediaRecorder
   */
  async initialize(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Minimum for good quality
        },
      });

      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus', // Good compression, wide support
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };
    } catch (error) {
      throw new Error(`Microphone access failed: ${error.message}`);
    }
  }

  /**
   * Start recording audio
   */
  startRecording(): void {
    if (!this.mediaRecorder) {
      throw new Error('MediaRecorder not initialized');
    }

    this.audioChunks = [];
    this.mediaRecorder.start();
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('MediaRecorder not initialized'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioChunks = [];
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    this.mediaRecorder = null;
    this.audioChunks = [];
  }
}
```

## 12.5 Web Audio API for Visualization

```typescript
// src/services/audio/audioProcessor.ts
export class AudioProcessor {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private dataArray: Uint8Array | null = null;

  /**
   * Initialize audio context and get microphone stream
   */
  async initialize(): Promise<void> {
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000, // Minimum required per NFR19
        } 
      });

      this.microphone = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;

      this.microphone.connect(this.analyser);
      
      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
    } catch (error) {
      throw new Error(`Failed to initialize audio: ${error}`);
    }
  }

  /**
   * Get current audio level (0-100)
   */
  getAudioLevel(): number {
    if (!this.analyser || !this.dataArray) return 0;

    this.analyser.getByteFrequencyData(this.dataArray);
    
    // Calculate average amplitude
    const sum = this.dataArray.reduce((acc, val) => acc + val, 0);
    const average = sum / this.dataArray.length;
    
    // Normalize to 0-100
    return Math.min(100, (average / 255) * 100);
  }

  /**
   * Get waveform data for visualization
   */
  getWaveformData(): Uint8Array {
    if (!this.analyser || !this.dataArray) return new Uint8Array(0);
    
    this.analyser.getByteTimeDomainData(this.dataArray);
    return this.dataArray;
  }

  /**
   * Check if audio input is detected
   */
  hasAudioInput(): boolean {
    const level = this.getAudioLevel();
    return level > 5; // Threshold for detecting sound
  }

  /**
   * Cleanup audio resources
   */
  cleanup(): void {
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.analyser = null;
    this.dataArray = null;
  }
}
```

## 12.4 WebRTC Audio Streaming

```typescript
// src/services/audio/webRTCHandler.ts
export class WebRTCHandler {
  private peerConnection: RTCPeerConnection | null = null;
  private dataChannel: RTCDataChannel | null = null;
  private localStream: MediaStream | null = null;

  /**
   * Initialize WebRTC peer connection
   */
  async initialize(onTrack: (stream: MediaStream) => void): Promise<void> {
    const configuration: RTCConfiguration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
      ],
    };

    this.peerConnection = new RTCPeerConnection(configuration);

    // Handle incoming tracks
    this.peerConnection.ontrack = (event) => {
      onTrack(event.streams[0]);
    };

    // Handle ICE candidates
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        // Send candidate to signaling server
        this.sendSignalingMessage('ice-candidate', event.candidate);
      }
    };

    // Get local media stream
    this.localStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      },
    });

    // Add tracks to peer connection
    this.localStream.getTracks().forEach((track) => {
      if (this.peerConnection && this.localStream) {
        this.peerConnection.addTrack(track, this.localStream);
      }
    });
  }

  /**
   * Create WebRTC offer
   */
  async createOffer(): Promise<RTCSessionDescriptionInit> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    const offer = await this.peerConnection.createOffer();
    await this.peerConnection.setLocalDescription(offer);
    return offer;
  }

  /**
   * Handle WebRTC answer
   */
  async handleAnswer(answer: RTCSessionDescriptionInit): Promise<void> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
  }

  /**
   * Add ICE candidate
   */
  async addIceCandidate(candidate: RTCIceCandidateInit): Promise<void> {
    if (!this.peerConnection) {
      throw new Error('Peer connection not initialized');
    }

    await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
  }

  /**
   * Monitor connection quality
   */
  async getConnectionStats(): Promise<RTCStatsReport | null> {
    if (!this.peerConnection) return null;

    return await this.peerConnection.getStats();
  }

  /**
   * Send signaling message (implement based on backend)
   */
  private sendSignalingMessage(type: string, data: any): void {
    // TODO: Implement WebSocket or HTTP signaling
    console.log('Signaling message:', type, data);
  }

  /**
   * Cleanup WebRTC resources
   */
  cleanup(): void {
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
      this.localStream = null;
    }
    if (this.dataChannel) {
      this.dataChannel.close();
      this.dataChannel = null;
    }
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
  }
}
```

## 12.6 Audio Recording Hook

```typescript
// src/features/interview/hooks/useAudioRecording.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { AudioProcessor } from '@/services/audio/audioProcessor';
import { AudioCaptureService } from '@/services/audio/audioCapture';
import { useInterviewStore } from '../store/interviewStore';
import { useSendAudio } from './useInterviewQueries';

export const useAudioRecording = (interviewId: string) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const audioProcessor = useRef<AudioProcessor>(new AudioProcessor());
  const audioCapture = useRef<AudioCaptureService>(new AudioCaptureService());
  const animationFrame = useRef<number>();

  const { setRecording, setAudioLevel: setStoreAudioLevel } = useInterviewStore();
  const sendAudioMutation = useSendAudio(interviewId);

  // Update audio level visualization
  const updateAudioLevel = useCallback(() => {
    if (!isRecording) return;

    const level = audioProcessor.current.getAudioLevel();
    setAudioLevel(level);
    setStoreAudioLevel(level);

    animationFrame.current = requestAnimationFrame(updateAudioLevel);
  }, [isRecording, setStoreAudioLevel]);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      setError(null);
      
      // Initialize audio processor for visualization
      await audioProcessor.current.initialize();
      
      // Initialize audio capture for recording
      await audioCapture.current.initialize();
      audioCapture.current.startRecording();

      setIsRecording(true);
      setRecording(true);
      updateAudioLevel();
    } catch (err) {
      setError(`Failed to start recording: ${err.message}`);
    }
  }, [setRecording, updateAudioLevel]);

  // Stop recording and send to backend
  const stopRecording = useCallback(async () => {
    if (animationFrame.current) {
      cancelAnimationFrame(animationFrame.current);
    }

    try {
      // Get audio blob
      const audioBlob = await audioCapture.current.stopRecording();
      
      // Send to backend for transcription
      await sendAudioMutation.mutateAsync(audioBlob);
      
    } catch (err) {
      setError(`Failed to process audio: ${err.message}`);
    } finally {
      audioProcessor.current.cleanup();
      audioCapture.current.cleanup();

      setIsRecording(false);
      setRecording(false);
      setAudioLevel(0);
      setStoreAudioLevel(0);
    }
  }, [setRecording, setStoreAudioLevel, sendAudioMutation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, [isRecording, stopRecording]);

  return {
    isRecording,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    isProcessing: sendAudioMutation.isPending,
  };
};
```

## 12.7 Audio Quality Guidelines

**Minimum Requirements:**
- Sample rate: 16kHz minimum
- Audio format: WebM with Opus codec (good compression, wide support)
- Processing time: <3s for speech-to-text (OpenAI Whisper)
- Synthesis time: <2s for text-to-speech (OpenAI TTS)

**Best Practices:**
- Enable echo cancellation and noise suppression
- Use appropriate voice selection for natural TTS (nova, alloy for professional tone)
- Implement audio buffering for smooth playback
- Monitor audio quality metrics in real-time
- Provide visual feedback for all audio states
- Gracefully degrade to text mode on failures

**Cost Optimization:**
- Cache frequently used TTS responses (greetings, common questions)
- Monitor token usage for Whisper transcriptions
- Use `tts-1` model for MVP, upgrade to `tts-1-hd` if quality issues arise

**Future Optimizations:**
- Consider Azure Speech Services for real-time streaming (<1s latency)
- Evaluate GCP Speech-to-Text for specific regional requirements
- Implement WebRTC for ultra-low latency if customer feedback demands it

---
