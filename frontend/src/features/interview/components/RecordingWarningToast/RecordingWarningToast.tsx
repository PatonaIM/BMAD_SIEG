/**
 * Recording Warning Toast Component
 * 
 * Displays a one-time warning toast when video recording starts
 * Auto-dismisses after 5 seconds
 */

import { useEffect } from 'react'
import { AlertCircle } from 'lucide-react'
import { useToast } from '@/components/ui/use-toast'

export interface RecordingWarningToastProps {
  sessionId: string
  isRecording: boolean
}

/**
 * Recording Warning Toast
 * 
 * Shows warning when video recording starts (first 5 seconds)
 * Only displays once per session using localStorage
 */
export function RecordingWarningToast({ 
  sessionId, 
  isRecording 
}: RecordingWarningToastProps) {
  const { toast } = useToast()

  useEffect(() => {
    if (!isRecording || !sessionId) return

    // Check if warning already shown for this session
    const storageKey = `interview_recording_warning_shown_${sessionId}`
    const warningShown = localStorage.getItem(storageKey)

    if (warningShown === 'true') {
      return // Already shown
    }

    // Show toast
    toast({
      title: (
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          <span>Recording in progress</span>
        </div>
      ),
      description: 'This interview is being recorded for recruiter review.',
      duration: 5000, // 5 seconds
      className: 'top-16', // Position below RecordingIndicator
    })

    // Mark as shown
    localStorage.setItem(storageKey, 'true')
  }, [isRecording, sessionId, toast])

  return null // This component doesn't render anything (toast is handled by provider)
}
