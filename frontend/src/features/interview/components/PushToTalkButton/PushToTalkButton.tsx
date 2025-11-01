import React from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import type { AudioCaptureState } from '../../hooks/useAudioCapture';

export interface PushToTalkButtonProps {
  state: AudioCaptureState;
  error?: string | null;
  onMouseDown?: () => void;
  onMouseUp?: () => void;
  onTouchStart?: () => void;
  onTouchEnd?: () => void;
  disabled?: boolean;
  className?: string;
}

/**
 * Push-to-talk button component for audio recording
 * Hold to speak, release to submit
 */
export function PushToTalkButton({
  state,
  error,
  onMouseDown,
  onMouseUp,
  onTouchStart,
  onTouchEnd,
  disabled = false,
  className = '',
}: PushToTalkButtonProps) {
  // Prevent default touch behavior to avoid accidental double-recording
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    onTouchStart?.();
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    onTouchEnd?.();
  };

  // Forward mouse events to parent handlers
  // Parent handlers will manage permission checks and state transitions
  const handleMouseDown = () => {
    if (!disabled) {
      onMouseDown?.();
    }
  };

  const handleMouseUp = () => {
    if (!disabled) {
      onMouseUp?.();
    }
  };

  // Determine button appearance based on state
  const getButtonStyles = () => {
    const baseStyles = 'flex items-center justify-center gap-2 px-6 py-4 rounded-lg font-semibold transition-all duration-200 select-none touch-none';
    
    switch (state) {
      case 'recording':
        return `${baseStyles} bg-red-500 text-white shadow-lg shadow-red-500/50 animate-pulse`;
      case 'processing':
        return `${baseStyles} bg-gray-400 text-white cursor-wait`;
      case 'error':
        return `${baseStyles} bg-red-100 text-red-700 cursor-not-allowed`;
      case 'idle':
      default:
        return `${baseStyles} bg-gray-200 text-gray-700 hover:bg-gray-300 active:bg-gray-400`;
    }
  };

  const getIcon = () => {
    switch (state) {
      case 'recording':
        return <Mic className="w-6 h-6" />;
      case 'processing':
        return <Loader2 className="w-6 h-6 animate-spin" />;
      case 'error':
        return <MicOff className="w-6 h-6" />;
      case 'idle':
      default:
        return <Mic className="w-6 h-6" />;
    }
  };

  const getLabel = () => {
    switch (state) {
      case 'recording':
        return 'Release to Submit';
      case 'processing':
        return 'Processing...';
      case 'error':
        return error || 'Error';
      case 'idle':
      default:
        return 'Hold to Speak';
    }
  };

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      <button
        type="button"
        className={getButtonStyles()}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        disabled={disabled || state === 'processing'}
        aria-label={getLabel()}
        aria-pressed={state === 'recording'}
      >
        {getIcon()}
        <span>{getLabel()}</span>
      </button>
      
      {error && state === 'error' && (
        <p className="text-sm text-red-600 text-center max-w-md">
          {error}
        </p>
      )}
    </div>
  );
}
