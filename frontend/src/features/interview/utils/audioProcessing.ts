/**
 * Audio Processing Utilities
 * 
 * Utilities for converting browser audio to PCM16 format at 24kHz
 * required by OpenAI Realtime API, and for playback of received audio.
 */

/**
 * Resample audio buffer to PCM16 at target sample rate
 * 
 * @param audioBuffer - Input AudioBuffer (typically 48kHz from browser)
 * @param targetSampleRate - Target sample rate (24000 for OpenAI Realtime API)
 * @returns Int16Array containing PCM16 audio data
 * 
 * @example
 * ```typescript
 * const audioContext = new AudioContext()
 * const arrayBuffer = await audioFile.arrayBuffer()
 * const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
 * const pcm16 = await resampleToPCM16(audioBuffer, 24000)
 * ```
 */
export async function resampleToPCM16(
  audioBuffer: AudioBuffer,
  targetSampleRate: number = 24000
): Promise<Int16Array> {
  // Create offline audio context for resampling
  const offlineContext = new OfflineAudioContext(
    1, // mono
    Math.ceil(audioBuffer.duration * targetSampleRate),
    targetSampleRate
  )
  
  // Create buffer source
  const source = offlineContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(offlineContext.destination)
  source.start(0)
  
  // Render resampled audio
  const resampledBuffer = await offlineContext.startRendering()
  const float32Data = resampledBuffer.getChannelData(0)
  
  // Convert Float32 to Int16 (PCM16)
  return float32ToPCM16(float32Data)
}

/**
 * Convert Float32 audio data to PCM16 (Int16Array)
 * 
 * @param float32Data - Float32Array audio data (range: -1.0 to 1.0)
 * @returns Int16Array PCM16 audio data
 */
export function float32ToPCM16(float32Data: Float32Array): Int16Array {
  const pcm16 = new Int16Array(float32Data.length)
  
  for (let i = 0; i < float32Data.length; i++) {
    // Clamp to [-1, 1] range
    const sample = Math.max(-1, Math.min(1, float32Data[i]))
    // Convert to 16-bit integer
    pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
  }
  
  return pcm16
}

/**
 * Encode PCM16 data to base64 string for WebSocket transmission
 * 
 * @param pcm16Data - Int16Array PCM16 audio data
 * @returns Base64 encoded string
 */
export function encodeToBase64(pcm16Data: Int16Array): string {
  const uint8Array = new Uint8Array(pcm16Data.buffer)
  let binary = ''
  for (let i = 0; i < uint8Array.length; i++) {
    binary += String.fromCharCode(uint8Array[i])
  }
  return btoa(binary)
}

/**
 * Decode base64 string to PCM16 audio data
 * 
 * @param base64String - Base64 encoded audio data
 * @returns Int16Array PCM16 audio data
 */
export function decodeFromBase64(base64String: string): Int16Array {
  const binaryString = atob(base64String)
  const uint8Array = new Uint8Array(binaryString.length)
  
  for (let i = 0; i < binaryString.length; i++) {
    uint8Array[i] = binaryString.charCodeAt(i)
  }
  
  return new Int16Array(uint8Array.buffer)
}

/**
 * Convert PCM16 to Float32 for Web Audio API playback
 * 
 * @param pcm16Data - Int16Array PCM16 audio data
 * @returns Float32Array audio data (range: -1.0 to 1.0)
 */
export function pcm16ToFloat32(pcm16Data: Int16Array): Float32Array {
  const float32 = new Float32Array(pcm16Data.length)
  
  for (let i = 0; i < pcm16Data.length; i++) {
    // Convert 16-bit integer to float
    float32[i] = pcm16Data[i] / (pcm16Data[i] < 0 ? 0x8000 : 0x7FFF)
  }
  
  return float32
}

/**
 * Audio Playback Queue
 * 
 * Manages smooth playback of audio chunks received from WebSocket
 * Buffers chunks and plays them sequentially without gaps
 */
export class AudioPlaybackQueue {
  private audioContext: AudioContext
  private queue: AudioBuffer[] = []
  private isPlaying: boolean = false
  private nextStartTime: number = 0
  private sampleRate: number
  private onPlaybackStart?: () => void
  private onPlaybackEnd?: () => void
  
  constructor(sampleRate: number = 24000, callbacks?: { onPlaybackStart?: () => void, onPlaybackEnd?: () => void }) {
    this.audioContext = new AudioContext({ sampleRate })
    this.sampleRate = sampleRate
    this.onPlaybackStart = callbacks?.onPlaybackStart
    this.onPlaybackEnd = callbacks?.onPlaybackEnd
  }
  
  /**
   * Initialize audio context (required for mobile browsers)
   * Call this after user interaction to bypass autoplay restrictions
   */
  async init(): Promise<void> {
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume()
    }
  }
  
  /**
   * Add audio chunk to playback queue
   * 
   * @param pcm16Data - PCM16 audio data
   */
  async enqueue(pcm16Data: Int16Array): Promise<void> {
    // Ensure audio context is running
    await this.init()
    
    // Convert PCM16 to Float32
    const float32Data = pcm16ToFloat32(pcm16Data)
    
    // Create AudioBuffer
    const audioBuffer = this.audioContext.createBuffer(
      1, // mono
      float32Data.length,
      this.sampleRate
    )
    audioBuffer.copyToChannel(float32Data, 0)
    
    // Add to queue
    this.queue.push(audioBuffer)
    
    // Start playback if not already playing
    if (!this.isPlaying) {
      this.playNext()
    }
  }
  
  /**
   * Add base64-encoded audio chunk to queue
   * 
   * @param base64Audio - Base64 encoded PCM16 audio
   */
  async enqueueBase64(base64Audio: string): Promise<void> {
    const pcm16Data = decodeFromBase64(base64Audio)
    await this.enqueue(pcm16Data)
  }
  
  /**
   * Play next audio chunk in queue
   */
  private playNext(): void {
    if (this.queue.length === 0) {
      this.isPlaying = false
      // Call onPlaybackEnd when queue is empty
      if (this.onPlaybackEnd) {
        this.onPlaybackEnd()
      }
      return
    }
    
    // Call onPlaybackStart when starting to play first chunk
    if (!this.isPlaying && this.onPlaybackStart) {
      this.onPlaybackStart()
    }
    
    this.isPlaying = true
    const audioBuffer = this.queue.shift()!
    
    // Create buffer source
    const source = this.audioContext.createBufferSource()
    source.buffer = audioBuffer
    source.connect(this.audioContext.destination)
    
    // Calculate start time for seamless playback
    const now = this.audioContext.currentTime
    const startTime = Math.max(now, this.nextStartTime)
    
    source.start(startTime)
    
    // Update next start time
    this.nextStartTime = startTime + audioBuffer.duration
    
    // Play next chunk when this one finishes
    source.onended = () => {
      this.playNext()
    }
  }
  
  /**
   * Clear playback queue and stop current playback
   */
  clear(): void {
    this.queue = []
    this.isPlaying = false
    this.nextStartTime = 0
  }
  
  /**
   * Get current audio level (0-100) for visualization
   * 
   * @returns Audio level as percentage
   */
  getAudioLevel(): number {
    // This is a simplified implementation
    // For real-time level detection, use AnalyserNode
    return 0
  }
  
  /**
   * Close audio context and cleanup resources
   */
  async close(): Promise<void> {
    this.clear()
    await this.audioContext.close()
  }
}

/**
 * Audio Level Monitor
 * 
 * Monitors microphone audio level for visual feedback
 */
export class AudioLevelMonitor {
  private audioContext: AudioContext
  private analyser: AnalyserNode | null = null
  private dataArray: Uint8Array | null = null
  private animationFrameId: number | null = null
  
  constructor() {
    this.audioContext = new AudioContext()
  }
  
  /**
   * Start monitoring audio from media stream
   * 
   * @param stream - MediaStream from getUserMedia
   * @param callback - Callback function receiving audio level (0-100)
   */
  start(stream: MediaStream, callback: (level: number) => void): void {
    // Create analyser node
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 256
    this.analyser.smoothingTimeConstant = 0.8
    
    const bufferLength = this.analyser.frequencyBinCount
    this.dataArray = new Uint8Array(bufferLength)
    
    // Connect stream to analyser
    const source = this.audioContext.createMediaStreamSource(stream)
    source.connect(this.analyser)
    
    // Start monitoring loop
    const monitor = () => {
      if (!this.analyser || !this.dataArray) return
      
      this.analyser.getByteFrequencyData(this.dataArray)
      
      // Calculate average level
      let sum = 0
      for (let i = 0; i < this.dataArray.length; i++) {
        sum += this.dataArray[i]
      }
      const average = sum / this.dataArray.length
      
      // Convert to 0-100 range
      const level = Math.min(100, (average / 255) * 100)
      
      callback(level)
      
      this.animationFrameId = requestAnimationFrame(monitor)
    }
    
    monitor()
  }
  
  /**
   * Stop monitoring
   */
  stop(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
    
    this.analyser = null
    this.dataArray = null
  }
  
  /**
   * Close audio context
   */
  async close(): Promise<void> {
    this.stop()
    await this.audioContext.close()
  }
}
