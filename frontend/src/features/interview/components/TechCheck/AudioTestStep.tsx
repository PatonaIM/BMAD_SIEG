"use client"

import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Mic, Play, Check } from 'lucide-react';
import { AudioLevelMeter } from '@/src/components/teamified/AudioLevelMeter/AudioLevelMeter';
import { PermissionDeniedHelp } from './PermissionDeniedHelp';
import { useMediaPermissions } from '@/src/hooks/useMediaPermissions';
import { useAudioCapture } from '../../hooks/useAudioCapture';

export interface AudioTestStepProps {
  onPass: () => void;
  onStop?: () => void;
}

type TestState = 'initial' | 'recording' | 'recorded' | 'playing' | 'confirmed';

/**
 * Audio test step component
 * Handles microphone permission, audio recording, playback, and confirmation
 */
export function AudioTestStep({ onPass, onStop }: AudioTestStepProps) {
  const [testState, setTestState] = useState<TestState>('initial');
  const [recordedAudio, setRecordedAudio] = useState<Blob | null>(null);
  const [isLevelPassing, setIsLevelPassing] = useState(false);
  
  const {
    microphoneStatus,
    microphoneStream,
    microphoneError,
    requestMicrophone,
    releaseMicrophone,
  } = useMediaPermissions();
  
  const {
    startRecording,
    stopRecording,
  } = useAudioCapture({ externalStream: microphoneStream });

  // Request permission on mount or when retry is clicked
  const handleRequestPermission = useCallback(async () => {
    await requestMicrophone();
  }, [requestMicrophone]);

  // Handle record button click
  const handleRecord = useCallback(async () => {
    setTestState('recording');
    setIsLevelPassing(false);
    
    // Start recording
    await startRecording();
    
    // Record for 3 seconds
    setTimeout(async () => {
      const blob = await stopRecording();
      if (blob) {
        setRecordedAudio(blob);
        setTestState('recorded');
      } else {
        setTestState('initial');
      }
    }, 3000);
  }, [startRecording, stopRecording]);

  // Handle playback
  const handlePlayback = useCallback(() => {
    if (!recordedAudio) return;
    
    setTestState('playing');
    const audio = new Audio(URL.createObjectURL(recordedAudio));
    
    audio.onended = () => {
      setTestState('recorded');
      URL.revokeObjectURL(audio.src);
    };
    
    audio.play();
  }, [recordedAudio]);

  // Handle confirmation
  const handleConfirm = useCallback(() => {
    setTestState('confirmed');
    onPass();
  }, [onPass]);

  // Handle stop/cancel test
  const handleStopTest = useCallback(() => {
    releaseMicrophone();
    setTestState('initial');
    setRecordedAudio(null);
    setIsLevelPassing(false);
    onStop?.();
  }, [releaseMicrophone, onStop]);

  // Show permission denied help
  if (microphoneStatus === 'denied') {
    return (
      <PermissionDeniedHelp
        deviceType="microphone"
        onRetry={handleRequestPermission}
      />
    );
  }

  // Show error state
  if (microphoneStatus === 'error' && microphoneError) {
    return (
      <Card className="p-6 border-yellow-200 dark:border-yellow-900 bg-yellow-50 dark:bg-yellow-950/30">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100">
            Microphone Error
          </h3>
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            {microphoneError}
          </p>
          <Button onClick={handleRequestPermission} variant="outline">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 flex flex-col h-full">
      <div className="flex flex-col flex-1 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Mic className="h-6 w-6" />
              Audio Test
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Test your microphone to ensure clear audio during the interview
            </p>
          </div>
          {/* Stop Test / Test Again button */}
          {microphoneStatus === 'granted' && (
            <Button
              onClick={handleStopTest}
              variant="ghost"
              size="sm"
              className="text-gray-600 hover:text-gray-800 hover:bg-gray-100"
            >
              {testState === 'confirmed' ? 'Test Again' : 'Stop Test'}
            </Button>
          )}
        </div>

        {/* Request permission */}
        {microphoneStatus === 'idle' && (
          <div className="flex flex-col flex-1 space-y-4">
            <p className="text-sm flex-1">
              Click the button below to grant microphone access.
            </p>
            <Button onClick={handleRequestPermission} size="lg" className="mt-auto">
              <Mic className="h-4 w-4 mr-2" />
              Enable Microphone
            </Button>
          </div>
        )}

        {/* Show audio level meter when permission granted */}
        {microphoneStatus === 'granted' && microphoneStream && testState === 'initial' && (
          <div className="flex flex-col flex-1 space-y-4">
            <div className="flex-1">
              <AudioLevelMeter
                stream={microphoneStream}
                onPassThreshold={setIsLevelPassing}
              />
            </div>
            
            {/* Primary action: Confirm audio quality */}
            <Button
              onClick={handleConfirm}
              size="lg"
              disabled={!isLevelPassing}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 mt-auto"
            >
              <Check className="h-4 w-4 mr-2" />
              {isLevelPassing ? 'Confirm Audio Quality' : 'Speak to enable confirmation'}
            </Button>

            {/* Optional: Record test audio */}
            {isLevelPassing && (
              <Button
                onClick={handleRecord}
                variant="outline"
                className="w-full"
              >
                <Mic className="h-4 w-4 mr-2" />
                Or Record Test Audio (3 seconds)
              </Button>
            )}
          </div>
        )}

        {/* Recording in progress */}
        {testState === 'recording' && (
          <div className="space-y-4">
            <div className="flex items-center justify-center p-8">
              <div className="relative">
                <div className="animate-ping absolute inline-flex h-16 w-16 rounded-full bg-red-400 opacity-75"></div>
                <div className="relative inline-flex h-16 w-16 rounded-full bg-red-500 items-center justify-center">
                  <Mic className="h-8 w-8 text-white" />
                </div>
              </div>
            </div>
            <p className="text-center text-lg font-medium">
              Recording... Speak clearly!
            </p>
          </div>
        )}

        {/* Recorded - show playback and confirm */}
        {(testState === 'recorded' || testState === 'playing') && (
          <div className="flex flex-col flex-1 space-y-4">
            <div className="flex-1 space-y-4">
              <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 rounded-lg">
                <p className="text-sm text-green-800 dark:text-green-200 flex items-center gap-2">
                  <Check className="h-4 w-4" />
                  Recording complete!
                </p>
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={handlePlayback}
                  variant="outline"
                  disabled={testState === 'playing'}
                  className="flex-1"
                >
                  <Play className="h-4 w-4 mr-2" />
                  {testState === 'playing' ? 'Playing...' : 'Play Back'}
                </Button>
                <Button
                  onClick={handleRecord}
                  variant="outline"
                  className="flex-1"
                >
                  <Mic className="h-4 w-4 mr-2" />
                  Record Again
                </Button>
              </div>
            </div>

            <Button
              onClick={handleConfirm}
              size="lg"
              className="w-full bg-green-600 hover:bg-green-700 mt-auto"
            >
              <Check className="h-4 w-4 mr-2" />
              Confirm Audio Quality
            </Button>
          </div>
        )}

        {/* Confirmed state */}
        {testState === 'confirmed' && (
          <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 rounded-lg">
            <p className="text-green-800 dark:text-green-200 flex items-center gap-2 font-medium">
              <Check className="h-5 w-5" />
              Audio test passed!
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
