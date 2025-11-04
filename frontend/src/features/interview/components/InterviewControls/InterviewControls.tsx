/**
 * Interview Controls Component
 * 
 * Minimal control bar with show/hide self-view and end interview buttons
 * Camera always records, but candidate can choose to see themselves or not
 * Supports keyboard shortcuts (V for view, Enter for done speaking)
 */

import { useEffect, useCallback } from 'react'
import { Eye, EyeOff, PhoneOff, Check } from 'lucide-react'

export interface InterviewControlsProps {
  isSelfViewVisible: boolean
  onToggleSelfView: () => void
  onEndInterview: () => void
  onDoneSpeaking?: () => void
  showDoneSpeaking?: boolean
  className?: string
}

export function InterviewControls({
  isSelfViewVisible,
  onToggleSelfView,
  onEndInterview,
  onDoneSpeaking,
  showDoneSpeaking = false,
  className = ''
}: InterviewControlsProps) {
  // Keyboard shortcuts handler
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Don't trigger shortcuts if user is typing in an input
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      return
    }

    // V: Toggle self-view visibility
    if (e.code === 'KeyV') {
      e.preventDefault()
      onToggleSelfView()
    }

    // Enter: Done speaking (manual turn completion)
    if (e.code === 'Enter' && showDoneSpeaking && onDoneSpeaking) {
      e.preventDefault()
      onDoneSpeaking()
    }

    // Escape: Focus on end interview button
    if (e.code === 'Escape') {
      e.preventDefault()
      const endButton = document.querySelector('.end-interview-button') as HTMLButtonElement
      endButton?.focus()
    }
  }, [onToggleSelfView, onDoneSpeaking, showDoneSpeaking])

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
      style={{ gridArea: 'controls' }}
      role="toolbar"
      aria-label="Interview Controls"
    >
      {/* Show/Hide Self-View button */}
      <button
        onClick={onToggleSelfView}
        className={`
          flex items-center justify-center w-14 h-14 rounded-full 
          transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
          ${isSelfViewVisible 
            ? 'bg-white/90 hover:bg-white text-gray-800' 
            : 'bg-gray-500 hover:bg-gray-600 text-white'}
        `}
        aria-label={isSelfViewVisible ? 'Hide self-view' : 'Show self-view'}
        title={isSelfViewVisible ? 'Hide self-view (V)' : 'Show self-view (V)'}
      >
        {isSelfViewVisible ? <Eye size={24} /> : <EyeOff size={24} />}
      </button>

      {/* Done Speaking button - Manual turn completion */}
      {showDoneSpeaking && onDoneSpeaking && (
        <button
          onClick={onDoneSpeaking}
          className="
            flex items-center gap-2 px-4 py-3 rounded-full 
            bg-green-500 hover:bg-green-600 text-white font-medium
            transition-all duration-150 hover:scale-105 active:scale-95 shadow-md
          "
          aria-label="Done speaking"
          title="Signal you're done speaking (Enter)"
        >
          <Check size={20} />
          <span className="text-sm">Done Speaking</span>
        </button>
      )}

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
