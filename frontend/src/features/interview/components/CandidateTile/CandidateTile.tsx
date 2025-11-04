/**
 * Candidate Tile Component
 * 
 * Video preview tile for candidate's self-view with toggle visibility
 */

import { useEffect, useRef, useState } from 'react'
import { Eye, EyeOff, Video } from 'lucide-react'

export interface CandidateTileProps {
  videoStream: MediaStream | null
  isVisible: boolean
  onToggleVisibility: () => void
  isRecording: boolean
  className?: string
}

export function CandidateTile({
  videoStream,
  isVisible,
  onToggleVisibility,
  isRecording,
  className = ''
}: CandidateTileProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isVideoReady, setIsVideoReady] = useState(false)

  // Set video stream when available
  useEffect(() => {
    if (videoRef.current && videoStream) {
      videoRef.current.srcObject = videoStream
      videoRef.current.onloadedmetadata = () => {
        videoRef.current?.play().catch(err => {
          console.error('Failed to play video:', err)
        })
        setIsVideoReady(true)
      }
    }
  }, [videoStream])

  return (
    <div 
      className={`
        relative w-full h-full rounded-xl overflow-hidden bg-black 
        shadow-lg border-2 border-white/10
        ${className}
      `}
      style={{ gridArea: 'candidate-tile' }}
      role="region"
      aria-label="Your Camera"
    >
      {/* Video element */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full h-full object-cover transition-opacity duration-200"
        style={{ opacity: isVisible ? 1 : 0 }}
      />

      {/* Hidden state overlay */}
      {!isVisible && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/80 text-white z-10">
          <EyeOff className="w-8 h-8 opacity-60 max-md:w-6 max-md:h-6" />
          <span className="text-sm opacity-60 max-md:text-xs">Camera Hidden</span>
        </div>
      )}

      {/* Controls overlay */}
      <div className="absolute bottom-3 right-3 flex gap-2 z-20 max-md:bottom-2 max-md:right-2 max-md:gap-1.5">
        {/* Toggle visibility button */}
        <button
          onClick={onToggleVisibility}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white/90 hover:bg-white 
                     transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
                     max-md:w-8 max-md:h-8"
          aria-label={isVisible ? 'Hide self-view' : 'Show self-view'}
          title={isVisible ? 'Hide self-view' : 'Show self-view'}
        >
          {isVisible ? <Eye size={20} className="max-md:w-4 max-md:h-4" /> : <EyeOff size={20} className="max-md:w-4 max-md:h-4" />}
        </button>

        {/* Camera active indicator */}
        {isRecording && (
          <div 
            className="flex items-center justify-center w-10 h-10 rounded-full bg-red-500/90 text-white shadow-md animate-pulse
                       max-md:w-8 max-md:h-8"
            aria-label="Camera is active"
            title="Camera is recording"
          >
            <Video size={16} className="max-md:w-3.5 max-md:h-3.5" />
          </div>
        )}
      </div>

      {/* No video placeholder */}
      {!videoStream && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-white/30 text-sm">
          <Video size={48} opacity={0.3} className="max-md:w-8 max-md:h-8" />
          <span className="max-md:text-xs">No camera</span>
        </div>
      )}
    </div>
  )
}
