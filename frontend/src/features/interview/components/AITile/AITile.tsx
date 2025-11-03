/**
 * AI Tile Component
 * 
 * Large tile containing AI presence orb, captions, and state indicators
 */

import { AIPresenceOrb, type OrbState } from '../AIPresenceOrb'
import { CaptionDisplay } from '../CaptionDisplay'
import { RecordingIndicator } from '../RecordingIndicator'
import type { ConnectionState } from '../../types/interview.types'

export interface AITileProps {
  orbState: OrbState
  audioLevel: number
  caption: string | null
  showCaption: boolean
  captionsEnabled: boolean
  onToggleCaptions: () => void
  connectionState: ConnectionState
  isRecording: boolean
  className?: string
}

export function AITile({
  orbState,
  audioLevel,
  caption,
  showCaption,
  captionsEnabled,
  onToggleCaptions,
  connectionState,
  isRecording,
  className = ''
}: AITileProps) {
  return (
    <div 
      className={`relative flex flex-col items-center justify-center rounded-2xl overflow-hidden shadow-lg ${className}`}
      style={{ gridArea: 'ai-tile' }}
      role="region"
      aria-label="AI Interviewer"
    >
      {/* Background gradient */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          background: 'linear-gradient(135deg, rgba(161, 106, 232, 0.1) 0%, rgba(29, 209, 161, 0.05) 100%)'
        }}
      />

      {/* AI Presence Orb - centered */}
      <div className="relative z-10 flex items-center justify-center">
        <AIPresenceOrb 
          state={orbState}
          audioLevel={audioLevel}
          size="lg"
        />
      </div>

      {/* State indicators - top right */}
      <div className="absolute top-4 right-4 flex gap-3 z-20">
        {/* Connection state badge */}
        {connectionState === 'connected' && (
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/95 shadow-md text-sm font-medium" aria-label="Connected">
            <div className="w-2 h-2 rounded-full bg-[#1DD1A1] animate-pulse" />
            <span className="hidden md:inline">Connected</span>
          </div>
        )}
        {connectionState === 'connecting' && (
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/95 shadow-md text-sm font-medium" aria-label="Connecting">
            <div className="w-2 h-2 rounded-full bg-[#FFA502] animate-pulse" />
            <span className="hidden md:inline">Connecting...</span>
          </div>
        )}
        {connectionState === 'error' && (
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white/95 shadow-md text-sm font-medium" aria-label="Connection Error">
            <div className="w-2 h-2 rounded-full bg-[#EF4444]" />
            <span className="hidden md:inline">Error</span>
          </div>
        )}

        {/* Recording indicator */}
        {isRecording && (
          <RecordingIndicator isRecording={isRecording} />
        )}
      </div>

      {/* Caption display - bottom third */}
      {captionsEnabled && (
        <div className="absolute bottom-0 left-0 right-0 h-1/3 flex items-end justify-center px-6 pb-6 z-20">
          <CaptionDisplay
            text={caption}
            isVisible={showCaption}
            enabled={captionsEnabled}
            onToggleEnabled={onToggleCaptions}
          />
        </div>
      )}
    </div>
  )
}
