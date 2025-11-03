/**
 * Interview Controls Component
 * 
 * Minimal control bar with mute, camera toggle, and end interview buttons
 * Supports keyboard shortcuts (Space, C)
 */

import { useEffect, useCallback } from 'react'
import { Mic, MicOff, Video, VideoOff, PhoneOff } from 'lucide-react'

export interface InterviewControlsProps {
  isMuted: boolean
  isCameraOn: boolean
  onToggleMute: () => void
  onToggleCamera: () => void
  onEndInterview: () => void
  className?: string
}

export function InterviewControls({
  isMuted,
  isCameraOn,
  onToggleMute,
  onToggleCamera,
  onEndInterview,
  className = ''
}: InterviewControlsProps) {
  // Keyboard shortcuts handler
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Don't trigger shortcuts if user is typing in an input
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      return
    }

    // Space: Toggle mute
    if (e.code === 'Space') {
      e.preventDefault()
      onToggleMute()
    }

    // V: Toggle video/camera (Story 2.5)
    if (e.code === 'KeyV') {
      e.preventDefault()
      onToggleCamera()
    }

    // Escape: Focus on end interview button
    if (e.code === 'Escape') {
      e.preventDefault()
      const endButton = document.querySelector('.end-interview-button') as HTMLButtonElement
      endButton?.focus()
    }
  }, [onToggleMute, onToggleCamera])

  // Register keyboard shortcuts
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])

  return (
    <div 
      className={`
        flex items-center justify-center gap-4 px-6 py-4
        bg-white/5 backdrop-blur-md rounded-2xl shadow-lg border border-white/10
        ${className}
      `}
      role="toolbar"
      aria-label="Interview Controls"
    >
      {/* Mute/Unmute button */}
      <button
        onClick={onToggleMute}
        className={`
          flex items-center justify-center w-14 h-14 rounded-full 
          transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
          ${isMuted 
            ? 'bg-red-500 hover:bg-red-600 text-white' 
            : 'bg-white/90 hover:bg-white text-gray-800'}
        `}
        aria-label={isMuted ? 'Unmute microphone' : 'Mute microphone'}
        title={isMuted ? 'Unmute (Space)' : 'Mute (Space)'}
      >
        {isMuted ? <MicOff size={24} /> : <Mic size={24} />}
      </button>

      {/* Camera toggle button */}
      <button
        onClick={onToggleCamera}
        className={`
          flex items-center justify-center w-14 h-14 rounded-full 
          transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
          ${!isCameraOn 
            ? 'bg-red-500 hover:bg-red-600 text-white' 
            : 'bg-white/90 hover:bg-white text-gray-800'}
        `}
        aria-label={isCameraOn ? 'Turn camera off' : 'Turn camera on'}
        title={isCameraOn ? 'Turn camera off (V)' : 'Turn camera on (V)'}
      >
        {isCameraOn ? <Video size={24} /> : <VideoOff size={24} />}
      </button>

      {/* End interview button */}
      <button
        onClick={onEndInterview}
        className="
          flex items-center justify-center w-14 h-14 rounded-full 
          bg-red-500 hover:bg-red-600 text-white
          transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
          end-interview-button
        "
        aria-label="End interview"
        title="End interview (Esc to focus)"
      >
        <PhoneOff size={24} />
      </button>
    </div>
  )
}
