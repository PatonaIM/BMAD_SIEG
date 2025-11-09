"use client"

import { useState, useCallback, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Video, Check, FlipHorizontal } from 'lucide-react';
import { PermissionDeniedHelp } from './PermissionDeniedHelp';
import { useMediaPermissions } from '@/src/hooks/useMediaPermissions';
import { cn } from '@/lib/utils';

export interface CameraTestStepProps {
  onPass: () => void;
  onStop?: () => void;
}

/**
 * Camera test step component
 * Handles camera permission, live preview, and resolution validation
 */
export function CameraTestStep({ onPass, onStop }: CameraTestStepProps) {
  const [isMirrored, setIsMirrored] = useState(true);
  const [isValidated, setIsValidated] = useState(false);
  const [canConfirm, setCanConfirm] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const {
    cameraStatus,
    cameraStream,
    cameraError,
    videoResolution,
    requestCamera,
    releaseCamera,
  } = useMediaPermissions();

  // Request permission on mount or when retry is clicked
  const handleRequestPermission = useCallback(async () => {
    await requestCamera();
    // Resolution check and onPass() now handled by useEffect
  }, [requestCamera]);

  // Attach stream to video element
  useEffect(() => {
    if (cameraStream && videoRef.current) {
      videoRef.current.srcObject = cameraStream;
    }
  }, [cameraStream]);

  // Auto-pass when resolution is detected and meets requirements
  useEffect(() => {
    if (videoResolution && cameraStatus === 'granted' && !canConfirm && !isValidated) {
      const meetsRequirements = videoResolution.width >= 640 && videoResolution.height >= 480;
      if (meetsRequirements) {
        // Enable confirmation button instead of auto-passing
        setCanConfirm(true);
      }
    }
  }, [videoResolution, cameraStatus, canConfirm, isValidated]);

  // Toggle mirror effect
  const handleToggleMirror = useCallback(() => {
    setIsMirrored(prev => !prev);
  }, []);

  // Handle confirmation
  const handleConfirm = useCallback(() => {
    setIsValidated(true);
    onPass();
  }, [onPass]);

  // Handle stop/cancel test
  const handleStopTest = useCallback(() => {
    releaseCamera();
    setIsValidated(false);
    setCanConfirm(false);
    onStop?.();
  }, [releaseCamera, onStop]);

  // Show permission denied help
  if (cameraStatus === 'denied') {
    return (
      <PermissionDeniedHelp
        deviceType="camera"
        onRetry={handleRequestPermission}
      />
    );
  }

  // Show error state
  if (cameraStatus === 'error' && cameraError) {
    return (
      <Card className="p-6 border-yellow-200 dark:border-yellow-900 bg-yellow-50 dark:bg-yellow-950/30">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100">
            Camera Error
          </h3>
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            {cameraError}
          </p>
          <Button onClick={handleRequestPermission} variant="outline">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  // Get resolution quality label
  const getResolutionQuality = () => {
    if (!videoResolution) return null;
    
    const { width, height } = videoResolution;
    if (width >= 1280 && height >= 720) return '720p HD';
    if (width >= 640 && height >= 480) return '480p SD';
    return 'Below 480p';
  };

  const resolutionQuality = getResolutionQuality();
  const meetsRequirements = videoResolution && videoResolution.width >= 640 && videoResolution.height >= 480;

  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="flex flex-col flex-1 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Video className="h-6 w-6" />
              Camera Test
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Test your camera to ensure clear video during the interview
            </p>
          </div>
          {/* Stop Test / Test Again button */}
          {cameraStatus === 'granted' && (
            <Button
              onClick={handleStopTest}
              variant="ghost"
              size="sm"
              className="text-gray-600 hover:text-gray-800 hover:bg-gray-100"
            >
              {isValidated ? 'Test Again' : 'Stop Test'}
            </Button>
          )}
        </div>

        {/* Request permission */}
        {cameraStatus === 'idle' && (
          <div className="flex flex-col flex-1 space-y-4">
            <p className="text-sm flex-1">
              Click the button below to grant camera access.
            </p>
            <Button onClick={handleRequestPermission} size="lg" className="mt-auto">
              <Video className="h-4 w-4 mr-2" />
              Enable Camera
            </Button>
          </div>
        )}

        {/* Show video preview when permission granted */}
        {cameraStatus === 'granted' && cameraStream && (
          <div className="flex flex-col flex-1 space-y-4">
            <div className="flex-1 space-y-4">
              {/* Video Preview */}
              <div className="relative bg-black rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={cn(
                    'w-full max-w-md mx-auto',
                    isMirrored && 'scale-x-[-1]'
                  )}
                />
                
                {/* Mirror Toggle Button */}
                <Button
                  onClick={handleToggleMirror}
                  variant="secondary"
                  size="sm"
                  className="absolute top-2 right-2"
                >
                  <FlipHorizontal className="h-4 w-4 mr-1" />
                  {isMirrored ? 'Unflip' : 'Mirror'}
                </Button>
              </div>

              {/* Resolution Info */}
              {videoResolution && (
                <div className={cn(
                  'p-4 rounded-lg border',
                  meetsRequirements 
                    ? 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-900'
                    : 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900'
                )}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">
                        Resolution: {videoResolution.width}x{videoResolution.height}
                      </p>
                      <p className="text-xs mt-1">
                        Quality: {resolutionQuality}
                      </p>
                    </div>
                    {meetsRequirements && (
                      <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
                    )}
                  </div>
                </div>
              )}

              {/* Pass/Fail Message */}
              {videoResolution && meetsRequirements && (
                <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 rounded-lg">
                  <p className="text-green-800 dark:text-green-200 flex items-center gap-2 font-medium">
                    <Check className="h-5 w-5" />
                    Camera test passed! Your video quality meets the requirements.
                  </p>
                </div>
              )}

              {videoResolution && !meetsRequirements && (
                <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 rounded-lg">
                  <p className="text-red-800 dark:text-red-200 font-medium">
                    Camera resolution too low
                  </p>
                  <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                    Minimum 640x480 (480p) required. Please use a different camera or check your camera settings.
                  </p>
                </div>
              )}
            </div>

            {/* Confirmation button - shown when camera meets requirements but not yet confirmed */}
            {canConfirm && !isValidated && (
              <Button
                onClick={handleConfirm}
                size="lg"
                className="w-full bg-green-600 hover:bg-green-700 mt-auto"
              >
                <Check className="h-4 w-4 mr-2" />
                Confirm Camera Quality
              </Button>
            )}

            {/* Confirmed state */}
            {isValidated && (
              <div className="p-4 bg-green-600 border border-green-700 rounded-lg mt-auto">
                <p className="text-white flex items-center gap-2 font-medium">
                  <Check className="h-5 w-5" />
                  Camera confirmed!
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
