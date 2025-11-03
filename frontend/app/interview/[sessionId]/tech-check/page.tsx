"use client"

import { useState, useCallback, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Check, AlertCircle, Info } from 'lucide-react';
import { AudioTestStep } from '@/src/features/interview/components/TechCheck/AudioTestStep';
import { CameraTestStep } from '@/src/features/interview/components/TechCheck/CameraTestStep';
import { VideoRecordingConsentModal } from '@/src/features/interview/components/VideoRecordingConsentModal';
import { useAuthStore } from '@/src/features/auth/store/authStore';
import { 
  submitTechCheckResults, 
  getBrowserInfo, 
  getDeviceName,
  type TechCheckRequest 
} from '@/src/features/interview/services/techCheckService';
import { useMediaPermissions } from '@/src/hooks/useMediaPermissions';

/**
 * Tech Check Page
 * Audio and camera testing on a single page before interview
 */
export default function TechCheckPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params?.sessionId as string | undefined;
  
  const [audioTestPassed, setAudioTestPassed] = useState(false);
  const [cameraTestPassed, setCameraTestPassed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showVideoConsentModal, setShowVideoConsentModal] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  
  const { isAuthenticated } = useAuthStore();
  const { microphoneStream, cameraStream, videoResolution } = useMediaPermissions();

  // Detect mobile on client-side to avoid hydration mismatch
  useEffect(() => {
    setIsMobile(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent));
    setIsMounted(true);
  }, []);

  // Handle audio test pass
  const handleAudioPass = useCallback(() => {
    setAudioTestPassed(true);
  }, []);

  // Handle camera test pass - show video consent modal if both tests pass
  const handleCameraPass = useCallback(() => {
    setCameraTestPassed(true);
  }, []);

  // Remove auto-open logic - user will click "Continue" button instead
  // Show consent modal when both tests pass
  // useEffect(() => {
  //   if (audioTestPassed && cameraTestPassed && !showVideoConsentModal && !hasShownConsent) {
  //     setShowVideoConsentModal(true);
  //     setHasShownConsent(true);
  //   }
  // }, [audioTestPassed, cameraTestPassed, showVideoConsentModal, hasShownConsent]);

  // Handle manual continue to interview
  const handleContinue = useCallback(() => {
    setShowVideoConsentModal(true);
  }, []);

  // Handle video consent decision
  const handleVideoConsent = useCallback(async (consent: boolean) => {
    setShowVideoConsentModal(false);
    
    // Submit consent to backend
    if (sessionId && sessionId !== 'preview') {
      try {
        // Use window.ENV only in client-side callback (not during render)
        const apiUrl = (window as any).ENV?.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
        
        await fetch(`${apiUrl}/api/v1/interviews/${sessionId}/consent`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(localStorage.getItem('auth_token') && {
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`
            })
          },
          body: JSON.stringify({ video_recording_consent: consent })
        })
        
        console.log(`✅ Video consent ${consent ? 'granted' : 'denied'}`)
      } catch (error) {
        console.error('Failed to submit video consent:', error)
      }
    }
    
    // After consent, proceed to start interview
    await startInterview();
  }, [sessionId]);

  // Handle go back to tech check from consent modal
  const handleGoBackToTechCheck = useCallback(() => {
    setShowVideoConsentModal(false);
    // Keep the test results, user can review or re-test
  }, []);

  // Handle start interview
  const startInterview = useCallback(async () => {
    if (!sessionId || sessionId === 'preview') {
      // Preview mode - just redirect to interview page
      router.push('/interview/start');
      return;
    }

    setIsSubmitting(true);

    try {
      // Gather tech check metadata
      const audioDeviceName = microphoneStream 
        ? await getDeviceName('audioinput', microphoneStream)
        : 'Unknown';
      
      const cameraDeviceName = cameraStream 
        ? await getDeviceName('videoinput', cameraStream)
        : 'Unknown';

      const techCheckData: TechCheckRequest = {
        audio_test_passed: audioTestPassed,
        camera_test_passed: cameraTestPassed,
        audio_metadata: {
          device_name: audioDeviceName,
          level: 0.75, // Could be tracked from AudioLevelMeter
          duration: 3.0,
        },
        camera_metadata: {
          device_name: cameraDeviceName,
          resolution: videoResolution 
            ? `${videoResolution.width}x${videoResolution.height}` 
            : 'Unknown',
          format: 'video/webm',
        },
        browser_info: getBrowserInfo(),
      };

      // Submit to backend (non-blocking)
      await submitTechCheckResults(sessionId, techCheckData);

      // Navigate to interview
      router.push(`/interview/${sessionId}`);
    } catch (error) {
      console.error('Error submitting tech check:', error);
      // Still allow navigation even if submission fails
      router.push(`/interview/${sessionId}`);
    } finally {
      setIsSubmitting(false);
    }
  }, [
    sessionId, 
    audioTestPassed, 
    cameraTestPassed, 
    microphoneStream, 
    cameraStream, 
    videoResolution, 
    router
  ]);

  // Handle reset
  const handleReset = useCallback(() => {
    setAudioTestPassed(false);
    setCameraTestPassed(false);
  }, []);

  // Don't render until mounted to avoid hydration mismatch
  if (!isMounted) {
    return null;
  }

  // Redirect to login if not authenticated (after mount)
  if (!isAuthenticated()) {
    router.push('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      {/* Video Recording Consent Modal */}
      <VideoRecordingConsentModal 
        open={showVideoConsentModal}
        onConsent={handleVideoConsent}
        onGoBack={handleGoBackToTechCheck}
        isSubmitting={false}
      />
      
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold">Pre-Interview Tech Check</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Test your audio and camera to ensure everything works properly
          </p>
        </div>

        {/* Progress Indicator */}
        <Card className="p-4">
          <div className="flex items-center justify-center gap-4">
            {/* Audio Step */}
            <div className="flex items-center gap-2">
              <div className={`
                flex items-center justify-center w-8 h-8 rounded-full transition-colors
                ${audioTestPassed ? 'bg-green-600 text-white' : 'bg-gray-300 dark:bg-gray-700 text-gray-600'}
              `}>
                {audioTestPassed ? <Check className="h-4 w-4" /> : '1'}
              </div>
              <span className={`text-sm font-medium ${audioTestPassed ? 'text-green-600 dark:text-green-400' : ''}`}>
                Microphone
              </span>
            </div>

            {/* Divider */}
            <div className="h-0.5 w-12 bg-gray-300 dark:bg-gray-700" />

            {/* Camera Step */}
            <div className="flex items-center gap-2">
              <div className={`
                flex items-center justify-center w-8 h-8 rounded-full transition-colors
                ${cameraTestPassed ? 'bg-green-600 text-white' : 'bg-gray-300 dark:bg-gray-700 text-gray-600'}
              `}>
                {cameraTestPassed ? <Check className="h-4 w-4" /> : '2'}
              </div>
              <span className={`text-sm font-medium ${cameraTestPassed ? 'text-green-600 dark:text-green-400' : ''}`}>
                Camera
              </span>
            </div>
          </div>
        </Card>

        {/* Success Message and Continue Button - shown when both tests pass */}
        {audioTestPassed && cameraTestPassed && (
          <>
            {/* Story 2.5: Recording privacy notice */}
            <Alert className="border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/30">
              <Info className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              <AlertDescription className="text-blue-800 dark:text-blue-200">
                This interview will be recorded with audio and video. 
                You can disable your camera at any time during the interview if needed.
              </AlertDescription>
            </Alert>

            <Card className="p-6 border-green-200 dark:border-green-900 bg-green-50 dark:bg-green-950/30">
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Check className="h-6 w-6 text-green-600 dark:text-green-400 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900 dark:text-green-100 text-lg">
                      All Checks Passed!
                    </h3>
                    <p className="text-sm text-green-800 dark:text-green-200 mt-1">
                      Your audio and camera are working perfectly. You're ready to start the interview.
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleContinue}
                  size="lg"
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  Continue to Interview
                </Button>
              </div>
            </Card>
          </>
        )}

        {/* Both Tests Side by Side */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Audio Test */}
          <AudioTestStep 
            onPass={handleAudioPass}
            onStop={() => setAudioTestPassed(false)}
          />

          {/* Camera Test */}
          <CameraTestStep 
            onPass={handleCameraPass}
            onStop={() => setCameraTestPassed(false)}
          />
        </div>

        {/* Mobile Notice */}
        {isMobile && (
          <Card className="p-4 border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950/30">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <p className="font-medium">Mobile Device Detected</p>
                <p className="mt-1">
                  For the best experience, please ensure you're in a quiet environment with good lighting.
                </p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
