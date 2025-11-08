/**
 * Video Recording Consent Modal Component
 * 
 * GDPR-compliant consent dialog for video recording
 * Displays before interview starts (after tech check)
 */

import { Video, Shield, Clock, Users, ArrowLeft, Loader2 } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

export interface VideoRecordingConsentModalProps {
  open: boolean
  onConsent: (consent: boolean) => void
  onGoBack?: () => void
  isSubmitting?: boolean
}

/**
 * Video Recording Consent Modal
 * 
 * Presents GDPR-compliant information about video recording:
 * - Purpose of recording
 * - Data retention policy
 * - Access controls
 * - Right to deletion
 */
export function VideoRecordingConsentModal({
  open,
  onConsent,
  onGoBack,
  isSubmitting = false
}: VideoRecordingConsentModalProps) {
  const handleAccept = () => {
    onConsent(true)
  }

  const handleClose = () => {
    // When dialog tries to close (X button or escape), treat it as going back
    if (onGoBack) {
      onGoBack()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && !isSubmitting && handleClose()}>
      <DialogContent className="max-w-lg" onPointerDownOutside={(e) => e.preventDefault()}>
        {/* Loading overlay - prevents user interaction during processing */}
        {isSubmitting && (
          <div className="absolute inset-0 bg-background/90 backdrop-blur-md z-50 flex items-center justify-center rounded-lg pointer-events-auto">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
              <p className="text-base font-semibold">Starting your interview...</p>
              <p className="text-xs text-muted-foreground">Please wait, do not close this window</p>
            </div>
          </div>
        )}
        
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Video className="h-5 w-5 text-blue-600" />
            Video Recording Consent
          </DialogTitle>
          <DialogDescription className="text-base">
            This interview will be recorded with audio and video for review purposes.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Purpose */}
          <div className="flex gap-3">
            <Users className="h-5 w-5 text-gray-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-sm mb-1">Who can view the recording?</h4>
              <p className="text-sm text-muted-foreground">
                Only recruiters from your organization can access the video. 
                It's used to review body language, professionalism, and presentation skills.
              </p>
            </div>
          </div>

          {/* Retention */}
          <div className="flex gap-3">
            <Clock className="h-5 w-5 text-gray-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-sm mb-1">How long is it stored?</h4>
              <p className="text-sm text-muted-foreground">
                Videos are automatically deleted after 30 days. 
                You can request immediate deletion at any time.
              </p>
            </div>
          </div>

          {/* Privacy */}
          <div className="flex gap-3">
            <Shield className="h-5 w-5 text-gray-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-sm mb-1">Your privacy rights</h4>
              <p className="text-sm text-muted-foreground">
                You have the right to access, review, and delete your recording at any time. 
                Contact support for assistance with GDPR requests.
              </p>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-row">
          {onGoBack && (
            <Button
              onClick={onGoBack}
              variant="outline"
              className="w-full sm:w-auto"
              disabled={isSubmitting}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tech Check
            </Button>
          )}
          <Button
            onClick={handleAccept}
            disabled={isSubmitting}
            className="w-full sm:flex-1"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Starting Interview...
              </>
            ) : (
              'I Consent - Start Interview'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
