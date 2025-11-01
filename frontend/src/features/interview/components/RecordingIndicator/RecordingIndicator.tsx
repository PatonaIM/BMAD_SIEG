/**
 * Recording Indicator Component
 * 
 * Displays a red recording indicator with pulsing animation
 * Informs candidate that video is being recorded
 */

import { Circle } from 'lucide-react'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

export interface RecordingIndicatorProps {
  isRecording: boolean
  className?: string
}

/**
 * Recording Indicator Component
 * 
 * Shows a pulsing red dot with "Recording" badge when active
 * Positioned in top-right corner, always visible
 */
export function RecordingIndicator({ 
  isRecording, 
  className = '' 
}: RecordingIndicatorProps) {
  if (!isRecording) {
    return null
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div 
            className={`fixed top-4 right-4 z-50 flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg shadow-lg ${className}`}
            role="status"
            aria-live="polite"
            aria-label="Video recording in progress"
          >
            {/* Pulsing red dot */}
            <div className="relative flex items-center justify-center">
              {/* Pulse ring animation */}
              <div className="absolute animate-ping">
                <Circle className="h-3 w-3 fill-red-500 text-red-500" />
              </div>
              
              {/* Static red dot */}
              <Circle className="relative h-3 w-3 fill-red-600 text-red-600" />
            </div>
            
            {/* Recording text */}
            <span className="text-sm font-medium text-red-700">
              Recording
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-xs">
          <p className="text-sm">
            This interview is being recorded for recruiter review. 
            Only recruiters from your organization can view the recording.
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
