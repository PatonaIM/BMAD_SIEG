/**
 * Caption History Modal Component
 * 
 * Displays the last 3 AI captions in a modal dialog
 * - Triggered by H key press
 * - Shows captions in reverse chronological order
 * - Displays timestamp for each caption
 * - Accessible with keyboard shortcuts
 */

import { useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { CaptionItem } from '../../utils/captionQueue'

export interface CaptionHistoryProps {
  captions: CaptionItem[]
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Format timestamp to readable time
 */
function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export function CaptionHistory({
  captions,
  open,
  onOpenChange
}: CaptionHistoryProps) {
  // Handle keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      // Toggle on H key (if not in input field)
      if (
        (event.key === 'h' || event.key === 'H') &&
        !isInputFocused()
      ) {
        event.preventDefault()
        onOpenChange(!open)
      }
      
      // Close on Escape
      if (event.key === 'Escape' && open) {
        event.preventDefault()
        onOpenChange(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, onOpenChange])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Caption History</DialogTitle>
          <DialogDescription>
            Recent AI captions from this interview session
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {captions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No captions yet
            </div>
          ) : (
            captions.map((caption, index) => (
              <div
                key={`${caption.timestamp}-${index}`}
                className="border-b border-border pb-4 last:border-b-0"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-muted-foreground uppercase">
                    AI
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatTimestamp(caption.timestamp)}
                  </span>
                </div>
                <p className="text-base text-foreground leading-relaxed">
                  {caption.text}
                </p>
              </div>
            ))
          )}
        </div>

        <div className="mt-6 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            Press <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">H</kbd> to toggle this dialog
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}

/**
 * Check if an input field is currently focused
 */
function isInputFocused(): boolean {
  const activeElement = document.activeElement
  return (
    activeElement instanceof HTMLInputElement ||
    activeElement instanceof HTMLTextAreaElement ||
    (activeElement instanceof HTMLElement && activeElement.isContentEditable)
  )
}
