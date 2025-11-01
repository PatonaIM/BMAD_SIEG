"use client"

import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

export interface AudioLevelMeterProps {
  stream: MediaStream | null;
  onPassThreshold?: (passed: boolean) => void;
  className?: string;
}

/**
 * AudioLevelMeter component displays a visual representation of audio input levels
 * Uses Web Audio API to analyze microphone input in real-time
 */
export function AudioLevelMeter({ stream, onPassThreshold, className }: AudioLevelMeterProps) {
  const [audioLevel, setAudioLevel] = useState(0);
  const [isPassing, setIsPassing] = useState(false);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const audioContextRef = useRef<AudioContext | undefined>(undefined);
  const analyserRef = useRef<AnalyserNode | undefined>(undefined);
  const sourceRef = useRef<MediaStreamAudioSourceNode | undefined>(undefined);
  const detectionStartTimeRef = useRef<number | null>(null);
  const isPassingRef = useRef(false);

  useEffect(() => {
    if (!stream) {
      // Clean up if stream is removed
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      setAudioLevel(0);
      setIsPassing(false);
      detectionStartTimeRef.current = null;
      isPassingRef.current = false;
      return;
    }

        // Create Audio Context and Analyser
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.8;

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    sourceRef.current = source;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const PASS_THRESHOLD = 10; // Simple threshold: 10 out of 255
    const PASS_DURATION = 1500; // 1.5 seconds of sustained audio

    function updateLevel() {
      if (!analyserRef.current) return;

      // Get frequency data (this actually works better for volume detection)
      analyserRef.current.getByteFrequencyData(dataArray);

      // Calculate average of all frequency bins
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const average = sum / dataArray.length;

      // Normalize to 0-1 range for display (0-255 -> 0-1)
      const normalizedLevel = average / 255;

      // Debug logging - show raw values
      console.log('🎤 Audio Level:', {
        average: average.toFixed(1),
        normalized: normalizedLevel.toFixed(3),
        percentage: `${(normalizedLevel * 100).toFixed(1)}%`,
        max: Math.max(...dataArray),
        threshold: `Need > ${PASS_THRESHOLD}`,
        rawSamples: `[${dataArray.slice(0, 5).join(', ')}...]`,
        sustained: detectionStartTimeRef.current ? `${((Date.now() - detectionStartTimeRef.current) / 1000).toFixed(1)}s / 1.5s` : 'waiting...'
      });

      setAudioLevel(normalizedLevel);

      // Check if audio level passes threshold (using raw average value)
      if (average > PASS_THRESHOLD) {
        if (detectionStartTimeRef.current === null) {
          detectionStartTimeRef.current = Date.now();
        } else {
          const duration = Date.now() - detectionStartTimeRef.current;
          if (duration >= PASS_DURATION && !isPassingRef.current) {
            isPassingRef.current = true;
            setIsPassing(true);
            onPassThreshold?.(true);
          }
        }
      } else {
        // Reset detection if audio drops below threshold
        if (detectionStartTimeRef.current !== null) {
          detectionStartTimeRef.current = null;
        }
      }

      animationFrameRef.current = requestAnimationFrame(updateLevel);
    }

    updateLevel();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContext.state !== 'closed') {
        audioContext.close();
      }
    };
  }, [stream, onPassThreshold]);

  // Calculate visual properties
  const levelPercentage = Math.min(audioLevel * 100, 100);
  const isDetecting = audioLevel > 0.1;

  // Color gradient based on level
  const getBarColor = () => {
    if (levelPercentage < 30) return 'bg-green-500';
    if (levelPercentage < 70) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className={cn('w-full max-w-md', className)}>
      <div className="space-y-2">
        {/* Audio Level Bar */}
        <div className="relative h-8 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-100 ease-out',
              getBarColor()
            )}
            style={{ width: `${levelPercentage}%` }}
          />
        </div>

        {/* Status Text */}
        <div className="flex justify-between items-center text-sm">
          <span className={cn(
            'font-medium',
            isDetecting ? 'text-green-600 dark:text-green-400' : 'text-gray-500'
          )}>
            {isDetecting ? '🎤 Audio detected' : 'Speak now...'}
          </span>
          <span className="text-gray-600 dark:text-gray-400">
            {Math.round(levelPercentage)}%
          </span>
        </div>

        {/* Pass Indicator */}
        {isPassing && (
          <div className="flex items-center gap-2 text-green-600 dark:text-green-400 text-sm font-medium">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Audio test passed!</span>
          </div>
        )}

        {/* Help Text */}
        {!isDetecting && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Speak clearly for 1.5 seconds to pass the audio test
          </p>
        )}
      </div>
    </div>
  );
}
