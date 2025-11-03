/**
 * Caption Display Component
 * 
 * Displays AI speech as real-time captions with fade animations
 * - Fade in when new caption appears (200ms)
 * - Persist while AI is speaking
 * - Fade out 3 seconds after AI finishes (300ms)
 */

import { Subtitles } from 'lucide-react'

export interface CaptionDisplayProps {
  text: string | null
  isVisible: boolean
  enabled: boolean
  onToggleEnabled: () => void
  className?: string
}

export function CaptionDisplay({
  text,
  isVisible,
  enabled,
  onToggleEnabled,
  className = ''
}: CaptionDisplayProps) {
  if (!enabled) {
    return null
  }

  return (
    <div 
      className={`flex items-center gap-3 px-6 py-4 max-w-4xl ${className}`}
      role="region"
      aria-label="AI Captions"
      aria-live="polite"
    >
      {/* Caption text */}
      {text && (
        <div 
          className={`
            flex-1 text-white text-lg font-light tracking-wide leading-relaxed
            transition-opacity duration-200
            ${isVisible ? 'opacity-100' : 'opacity-0'}
          `}
        >
          {text}
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={onToggleEnabled}
        className="flex items-center justify-center w-10 h-10 rounded-full 
                   bg-white/10 hover:bg-white/20 
                   transition-colors duration-150
                   text-white opacity-60 hover:opacity-100 flex-shrink-0
                   max-md:w-9 max-md:h-9"
        aria-label="Disable captions"
        title="Hide captions"
      >
        <Subtitles size={20} className="max-md:w-4 max-md:h-4" />
      </button>
    </div>
  )
}
