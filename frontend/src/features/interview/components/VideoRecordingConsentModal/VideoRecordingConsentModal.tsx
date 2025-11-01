/**
 * Video Recording Consent Modal Component
 * 
 * GDPR-compliant consent dialog for video recording
 * Displays before interview starts (after tech check)
 */

import { useState } from 'react'
import { Video, Shield, Clock, Users, ArrowLeft } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

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
  const [selectedChoice, setSelectedChoice] = useState<'video' | 'audio' | null>(null)

  const handleSubmit = () => {
    if (selectedChoice) {
      onConsent(selectedChoice === 'video')
    }
  }

  const handleClose = () => {
    // When dialog tries to close (X button or escape), treat it as going back
    if (onGoBack) {
      onGoBack()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="max-w-lg" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Video className="h-5 w-5 text-blue-600" />
            Video Recording Consent
          </DialogTitle>
          <DialogDescription className="text-base">
            We'd like to record this interview. Your choice will not affect your evaluation.
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

          {/* Choice Selection */}
          <Alert className="mt-6">
            <AlertDescription>
              <p className="font-medium mb-3">Please select one option:</p>
              <div className="space-y-2">
                <button
                  type="button"
                  onClick={() => setSelectedChoice('video')}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedChoice === 'video'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">I Consent to Video Recording</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Interview will be recorded with audio and video
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedChoice('audio')}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    selectedChoice === 'audio'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium">Audio Only (No Video)</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Only audio will be recorded, no video
                  </div>
                </button>
              </div>
            </AlertDescription>
          </Alert>
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-row">
          {onGoBack && (
            <Button
              onClick={onGoBack}
              variant="outline"
              className="w-full sm:w-auto"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Tech Check
            </Button>
          )}
          <Button
            onClick={handleSubmit}
            disabled={!selectedChoice || isSubmitting}
            className="w-full sm:flex-1"
          >
            {isSubmitting ? 'Saving...' : 'Continue to Interview'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
