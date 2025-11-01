/**
 * Audio Optimization Utilities
 * 
 * Performance optimizations for realtime audio streaming:
 * - Adaptive buffer sizing
 * - Audio chunk compression
 * - Network bandwidth monitoring
 * - Latency tracking
 */

/**
 * Audio Buffer Manager
 * 
 * Dynamically adjusts buffer size based on network conditions
 * to minimize latency while preventing audio glitches
 */
export class AudioBufferManager {
  private minBufferSize: number = 2 // Minimum 2 chunks
  private maxBufferSize: number = 10 // Maximum 10 chunks
  private currentBufferSize: number = 5 // Start with middle value
  private glitchCount: number = 0
  private latencyHistory: number[] = []
  
  /**
   * Report audio glitch (underrun)
   */
  reportGlitch(): void {
    this.glitchCount++
    
    // Increase buffer size if glitches detected
    if (this.glitchCount >= 2 && this.currentBufferSize < this.maxBufferSize) {
      this.currentBufferSize = Math.min(
        this.currentBufferSize + 1,
        this.maxBufferSize
      )
      console.info(`Audio buffer increased to ${this.currentBufferSize} chunks`)
      this.glitchCount = 0 // Reset counter
    }
  }
  
  /**
   * Report stable playback
   */
  reportStable(): void {
    this.glitchCount = 0
    
    // Gradually reduce buffer size for lower latency
    if (this.currentBufferSize > this.minBufferSize) {
      this.currentBufferSize = Math.max(
        this.currentBufferSize - 1,
        this.minBufferSize
      )
      console.info(`Audio buffer decreased to ${this.currentBufferSize} chunks`)
    }
  }
  
  /**
   * Record latency measurement
   */
  recordLatency(ms: number): void {
    this.latencyHistory.push(ms)
    
    // Keep only last 20 measurements
    if (this.latencyHistory.length > 20) {
      this.latencyHistory.shift()
    }
  }
  
  /**
   * Get current buffer size
   */
  getBufferSize(): number {
    return this.currentBufferSize
  }
  
  /**
   * Get average latency
   */
  getAverageLatency(): number | null {
    if (this.latencyHistory.length === 0) return null
    return this.latencyHistory.reduce((a, b) => a + b, 0) / this.latencyHistory.length
  }
  
  /**
   * Get 95th percentile latency
   */
  getP95Latency(): number | null {
    if (this.latencyHistory.length === 0) return null
    const sorted = [...this.latencyHistory].sort((a, b) => a - b)
    const idx = Math.floor(sorted.length * 0.95)
    return sorted[idx]
  }
}

/**
 * Bandwidth Monitor
 * 
 * Tracks network bandwidth usage for audio streaming
 */
export class BandwidthMonitor {
  private bytesSent: number = 0
  private bytesReceived: number = 0
  private startTime: number = Date.now()
  private checkpoints: Array<{ time: number; sent: number; received: number }> = []
  
  /**
   * Record bytes sent
   */
  recordSent(bytes: number): void {
    this.bytesSent += bytes
    this.addCheckpoint()
  }
  
  /**
   * Record bytes received
   */
  recordReceived(bytes: number): void {
    this.bytesReceived += bytes
    this.addCheckpoint()
  }
  
  /**
   * Add checkpoint for bandwidth calculation
   */
  private addCheckpoint(): void {
    this.checkpoints.push({
      time: Date.now(),
      sent: this.bytesSent,
      received: this.bytesReceived,
    })
    
    // Keep only last 60 seconds
    const cutoff = Date.now() - 60000
    this.checkpoints = this.checkpoints.filter(cp => cp.time > cutoff)
  }
  
  /**
   * Get current upload bandwidth (bytes per second)
   */
  getUploadBandwidth(): number {
    if (this.checkpoints.length < 2) return 0
    
    const recent = this.checkpoints.slice(-10)
    const duration = (recent[recent.length - 1].time - recent[0].time) / 1000
    const bytesSent = recent[recent.length - 1].sent - recent[0].sent
    
    return duration > 0 ? bytesSent / duration : 0
  }
  
  /**
   * Get current download bandwidth (bytes per second)
   */
  getDownloadBandwidth(): number {
    if (this.checkpoints.length < 2) return 0
    
    const recent = this.checkpoints.slice(-10)
    const duration = (recent[recent.length - 1].time - recent[0].time) / 1000
    const bytesReceived = recent[recent.length - 1].received - recent[0].received
    
    return duration > 0 ? bytesReceived / duration : 0
  }
  
  /**
   * Get total bandwidth usage stats
   */
  getStats(): {
    totalBytesSent: number
    totalBytesReceived: number
    durationSeconds: number
    uploadKbps: number
    downloadKbps: number
  } {
    const durationSeconds = (Date.now() - this.startTime) / 1000
    
    return {
      totalBytesSent: this.bytesSent,
      totalBytesReceived: this.bytesReceived,
      durationSeconds,
      uploadKbps: (this.getUploadBandwidth() * 8) / 1000,
      downloadKbps: (this.getDownloadBandwidth() * 8) / 1000,
    }
  }
  
  /**
   * Reset monitoring
   */
  reset(): void {
    this.bytesSent = 0
    this.bytesReceived = 0
    this.startTime = Date.now()
    this.checkpoints = []
  }
}

/**
 * Latency Tracker
 * 
 * Tracks WebSocket and AI response latencies
 */
export class LatencyTracker {
  private websocketLatencies: number[] = []
  private aiResponseLatencies: number[] = []
  private pendingMessages: Map<string, number> = new Map()
  
  /**
   * Start tracking a WebSocket message
   */
  startMessage(messageId: string): void {
    this.pendingMessages.set(messageId, Date.now())
  }
  
  /**
   * Complete tracking a WebSocket message
   */
  completeMessage(messageId: string): number | null {
    const startTime = this.pendingMessages.get(messageId)
    if (!startTime) return null
    
    const latency = Date.now() - startTime
    this.websocketLatencies.push(latency)
    this.pendingMessages.delete(messageId)
    
    // Keep only last 100 measurements
    if (this.websocketLatencies.length > 100) {
      this.websocketLatencies.shift()
    }
    
    return latency
  }
  
  /**
   * Record AI response latency
   */
  recordAIResponse(latencyMs: number): void {
    this.aiResponseLatencies.push(latencyMs)
    
    // Keep only last 100 measurements
    if (this.aiResponseLatencies.length > 100) {
      this.aiResponseLatencies.shift()
    }
  }
  
  /**
   * Get average WebSocket latency
   */
  getAverageWebSocketLatency(): number | null {
    if (this.websocketLatencies.length === 0) return null
    return this.websocketLatencies.reduce((a, b) => a + b, 0) / this.websocketLatencies.length
  }
  
  /**
   * Get average AI response latency
   */
  getAverageAILatency(): number | null {
    if (this.aiResponseLatencies.length === 0) return null
    return this.aiResponseLatencies.reduce((a, b) => a + b, 0) / this.aiResponseLatencies.length
  }
  
  /**
   * Get 95th percentile AI latency
   */
  getP95AILatency(): number | null {
    if (this.aiResponseLatencies.length === 0) return null
    const sorted = [...this.aiResponseLatencies].sort((a, b) => a - b)
    const idx = Math.floor(sorted.length * 0.95)
    return sorted[idx]
  }
  
  /**
   * Check if latency is degraded (>1s for 95th percentile)
   */
  isLatencyDegraded(): boolean {
    const p95 = this.getP95AILatency()
    return p95 !== null && p95 > 1000
  }
  
  /**
   * Get latency stats
   */
  getStats(): {
    averageWebSocketMs: number | null
    averageAIMs: number | null
    p95AIMs: number | null
    isDegraded: boolean
  } {
    return {
      averageWebSocketMs: this.getAverageWebSocketLatency(),
      averageAIMs: this.getAverageAILatency(),
      p95AIMs: this.getP95AILatency(),
      isDegraded: this.isLatencyDegraded(),
    }
  }
  
  /**
   * Reset tracking
   */
  reset(): void {
    this.websocketLatencies = []
    this.aiResponseLatencies = []
    this.pendingMessages.clear()
  }
}

/**
 * Performance Monitor
 * 
 * Comprehensive performance monitoring for realtime audio streaming
 */
export class PerformanceMonitor {
  private bufferManager: AudioBufferManager
  private bandwidthMonitor: BandwidthMonitor
  private latencyTracker: LatencyTracker
  private startTime: number = Date.now()
  
  constructor() {
    this.bufferManager = new AudioBufferManager()
    this.bandwidthMonitor = new BandwidthMonitor()
    this.latencyTracker = new LatencyTracker()
  }
  
  /**
   * Report audio glitch
   */
  reportGlitch(): void {
    this.bufferManager.reportGlitch()
  }
  
  /**
   * Report stable playback
   */
  reportStable(): void {
    this.bufferManager.reportStable()
  }
  
  /**
   * Record audio sent
   */
  recordAudioSent(bytes: number): void {
    this.bandwidthMonitor.recordSent(bytes)
  }
  
  /**
   * Record audio received
   */
  recordAudioReceived(bytes: number): void {
    this.bandwidthMonitor.recordReceived(bytes)
  }
  
  /**
   * Start tracking message latency
   */
  startMessage(messageId: string): void {
    this.latencyTracker.startMessage(messageId)
  }
  
  /**
   * Complete tracking message latency
   */
  completeMessage(messageId: string): number | null {
    return this.latencyTracker.completeMessage(messageId)
  }
  
  /**
   * Record AI response latency
   */
  recordAIResponse(latencyMs: number): void {
    this.latencyTracker.recordAIResponse(latencyMs)
    this.bufferManager.recordLatency(latencyMs)
  }
  
  /**
   * Get recommended buffer size
   */
  getBufferSize(): number {
    return this.bufferManager.getBufferSize()
  }
  
  /**
   * Get comprehensive performance summary
   */
  getSummary(): {
    sessionDurationSeconds: number
    bandwidth: {
      totalBytesSent: number
      totalBytesReceived: number
      durationSeconds: number
      uploadKbps: number
      downloadKbps: number
    }
    latency: {
      averageWebSocketMs: number | null
      averageAIMs: number | null
      p95AIMs: number | null
      isDegraded: boolean
    }
    bufferSize: number
  } {
    return {
      sessionDurationSeconds: (Date.now() - this.startTime) / 1000,
      bandwidth: this.bandwidthMonitor.getStats(),
      latency: this.latencyTracker.getStats(),
      bufferSize: this.bufferManager.getBufferSize(),
    }
  }
  
  /**
   * Log performance summary to console
   */
  logSummary(): void {
    const summary = this.getSummary()
    
    console.info('=== Realtime Audio Performance Summary ===')
    console.info(`Session Duration: ${summary.sessionDurationSeconds.toFixed(1)}s`)
    console.info(`\nBandwidth:`)
    console.info(`  Upload: ${summary.bandwidth.uploadKbps.toFixed(1)} Kbps`)
    console.info(`  Download: ${summary.bandwidth.downloadKbps.toFixed(1)} Kbps`)
    console.info(`  Total Sent: ${(summary.bandwidth.totalBytesSent / 1024).toFixed(1)} KB`)
    console.info(`  Total Received: ${(summary.bandwidth.totalBytesReceived / 1024).toFixed(1)} KB`)
    console.info(`\nLatency:`)
    console.info(`  WebSocket: ${summary.latency.averageWebSocketMs?.toFixed(1) || 'N/A'} ms (avg)`)
    console.info(`  AI Response: ${summary.latency.averageAIMs?.toFixed(1) || 'N/A'} ms (avg)`)
    console.info(`  AI Response P95: ${summary.latency.p95AIMs?.toFixed(1) || 'N/A'} ms`)
    console.info(`  Status: ${summary.latency.isDegraded ? '⚠️ DEGRADED' : '✅ OK'}`)
    console.info(`\nBuffer: ${summary.bufferSize} chunks`)
    console.info('=========================================')
  }
  
  /**
   * Reset all monitoring
   */
  reset(): void {
    this.bufferManager = new AudioBufferManager()
    this.bandwidthMonitor.reset()
    this.latencyTracker.reset()
    this.startTime = Date.now()
  }
}
