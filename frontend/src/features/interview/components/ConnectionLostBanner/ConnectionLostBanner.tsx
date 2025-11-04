/**
 * ConnectionLostBanner Component
 * 
 * Displays a banner when realtime WebSocket connection is lost,
 * with option to retry connection.
 */

import { AlertTriangle, RotateCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

export interface ConnectionLostBannerProps {
  /** Whether banner is visible */
  show: boolean
  /** Retry connection callback */
  onRetry: () => void
  /** Switch to text mode callback (deprecated - kept for compatibility) */
  onSwitchToText?: () => void
  /** Reconnection attempt count */
  attemptCount?: number
}

/**
 * Banner displayed when realtime connection is lost.
 * 
 * Features:
 * - Clear error indication with icon
 * - Retry button with attempt counter
 * - Responsive layout
 * 
 * @example
 * ```tsx
 * <ConnectionLostBanner
 *   show={connectionState === 'disconnected'}
 *   onRetry={() => realtime.connect()}
 *   attemptCount={3}
 * />
 * ```
 */
export function ConnectionLostBanner({
  show,
  onRetry,
  attemptCount = 0,
}: ConnectionLostBannerProps) {
  if (!show) return null

  return (
    <div
      className="fixed top-0 left-0 right-0 z-50 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800"
      role="alert"
      aria-live="assertive"
    >
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          {/* Error Message */}
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-yellow-900 dark:text-yellow-100">
                Connection Lost
              </p>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                {attemptCount > 0
                  ? `Attempting to reconnect... (${attemptCount} ${attemptCount === 1 ? 'attempt' : 'attempts'})`
                  : 'Your realtime voice connection was interrupted.'}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 ml-8 sm:ml-0">
            <Button
              size="sm"
              variant="default"
              onClick={onRetry}
              disabled={attemptCount > 0}
              className="bg-yellow-600 hover:bg-yellow-700 text-white"
            >
              <RotateCw className="h-4 w-4 mr-1.5" />
              {attemptCount > 0 ? 'Reconnecting...' : 'Retry Connection'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
