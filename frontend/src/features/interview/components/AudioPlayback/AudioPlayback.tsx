import { useEffect, useRef, useState } from 'react';
import { useToast } from '@/hooks/use-toast';

export interface AudioPlaybackProps {
  audioUrl: string | null;
  onPlaybackStart?: () => void;
  onPlaybackEnd?: () => void;
  onPlaybackError?: (error: Error) => void;
  autoPlay?: boolean;
  className?: string;
}

/**
 * Audio Playback Component
 * Uses HTML5 Audio element for playback
 * Auto-plays AI responses when audio URL is available
 */
export function AudioPlayback({
  audioUrl,
  onPlaybackStart,
  onPlaybackEnd,
  onPlaybackError,
  autoPlay = true,
  className = '',
}: AudioPlaybackProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (!audioUrl) {
      return;
    }

    // Create new audio element
    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    // Event handlers
    const handlePlay = () => {
      setIsPlaying(true);
      onPlaybackStart?.();
    };

    const handleEnded = () => {
      setIsPlaying(false);
      onPlaybackEnd?.();
    };

    const handleError = (e: Event) => {
      setIsPlaying(false);
      const error = new Error('Could not play audio. Reading text instead.');
      console.error('Audio playback error:', e);
      
      toast({
        variant: 'destructive',
        title: 'Audio Playback Failed',
        description: 'Could not play audio. Reading text instead.',
      });
      
      onPlaybackError?.(error);
    };

    // Attach event listeners
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    // Auto-play if enabled
    if (autoPlay) {
      audio.play().catch((err) => {
        console.error('Auto-play failed:', err);
        // Handle autoplay restrictions (iOS Safari, etc.)
        toast({
          title: 'Tap to Play Audio',
          description: 'Your browser blocked auto-play. Tap the play button.',
        });
        onPlaybackError?.(new Error('Auto-play blocked'));
      });
    }

    // Cleanup
    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
      audio.pause();
      audioRef.current = null;
    };
  }, [audioUrl, autoPlay, onPlaybackStart, onPlaybackEnd, onPlaybackError, toast]);

  // This component is hidden - audio plays automatically
  // Only used for programmatic control
  return (
    <div className={`hidden ${className}`} aria-live="polite" aria-atomic="true">
      {isPlaying && <span className="sr-only">AI is speaking</span>}
    </div>
  );
}
