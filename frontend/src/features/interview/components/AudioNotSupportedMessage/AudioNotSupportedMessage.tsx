/**
 * AudioNotSupportedMessage Component
 * 
 * Displays a message when browser doesn't support audio features,
 * with instructions to continue in text mode or use a supported browser.
 */

import { MicOff, Chrome, Globe, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export interface AudioNotSupportedMessageProps {
  /** Whether message is visible */
  show: boolean
  /** Switch to text mode callback */
  onSwitchToText: () => void
  /** Optional custom message */
  customMessage?: string
}

/**
 * Message displayed when audio is not supported in the browser.
 * 
 * Features:
 * - Clear explanation of the issue
 * - Browser compatibility information
 * - Text mode fallback option
 * - Responsive layout
 * 
 * @example
 * ```tsx
 * <AudioNotSupportedMessage
 *   show={!isAudioSupported}
 *   onSwitchToText={() => setInputMode('text')}
 * />
 * ```
 */
export function AudioNotSupportedMessage({
  show,
  onSwitchToText,
  customMessage,
}: AudioNotSupportedMessageProps) {
  if (!show) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <Card className="max-w-md w-full p-6 animate-in fade-in slide-in-from-bottom-4 duration-200">
        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="p-3 rounded-full bg-orange-100 dark:bg-orange-900/20">
            <MicOff className="h-8 w-8 text-orange-600 dark:text-orange-400" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-center mb-2">
          Audio Not Supported
        </h2>

        {/* Message */}
        <p className="text-sm text-muted-foreground text-center mb-6">
          {customMessage ||
            'Your browser does not support audio recording. This may be due to browser limitations or missing permissions.'}
        </p>

        {/* Supported Browsers */}
        <div className="bg-muted/50 rounded-lg p-4 mb-6">
          <p className="text-xs font-medium mb-3 text-center">
            Voice interviews work best on:
          </p>
          <div className="flex justify-center gap-6">
            <div className="flex flex-col items-center gap-1">
              <Chrome className="h-6 w-6 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Chrome</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Globe className="h-6 w-6 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Firefox</span>
            </div>
            <div className="flex flex-col items-center gap-1">
              <Globe className="h-6 w-6 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Safari</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <Button
            onClick={onSwitchToText}
            className="w-full"
            size="lg"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Continue with Text Chat
          </Button>
          <p className="text-xs text-center text-muted-foreground">
            You can still complete the interview by typing your responses.
          </p>
        </div>
      </Card>
    </div>
  )
}
