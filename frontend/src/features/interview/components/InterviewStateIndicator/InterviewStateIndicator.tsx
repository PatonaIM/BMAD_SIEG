import { Card } from '@/components/ui/card';
import { Headphones, Ear, Mic, Loader2 } from 'lucide-react';

export type InterviewState = 'ai_speaking' | 'ai_listening' | 'candidate_speaking' | 'processing';

export interface InterviewStateIndicatorProps {
  state: InterviewState;
  className?: string;
}

/**
 * Interview State Indicator Component
 * Displays current interview state with icon and text
 * Visual states: AI Speaking, AI Listening, Candidate Speaking, Processing
 */
export function InterviewStateIndicator({ state, className = '' }: InterviewStateIndicatorProps) {
  const getStateConfig = () => {
    switch (state) {
      case 'ai_speaking':
        return {
          icon: <Headphones className="w-5 h-5" />,
          text: 'AI is asking a question...',
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-500',
          textColor: 'text-purple-900',
        };
      case 'ai_listening':
        return {
          icon: <Ear className="w-5 h-5" />,
          text: 'Your turn to speak',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-500',
          textColor: 'text-blue-900',
        };
      case 'candidate_speaking':
        return {
          icon: <Mic className="w-5 h-5" />,
          text: 'Recording your answer...',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-500',
          textColor: 'text-red-900',
          pulse: true,
        };
      case 'processing':
        return {
          icon: <Loader2 className="w-5 h-5 animate-spin" />,
          text: 'Processing response...',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-400',
          textColor: 'text-gray-900',
        };
    }
  };

  const config = getStateConfig();

  return (
    <Card
      className={`
        ${config.bgColor} 
        ${config.borderColor} 
        border-2
        p-3 md:p-4
        transition-all 
        duration-200 
        ease-in-out
        ${config.pulse ? 'animate-pulse' : ''}
        ${className}
      `}
      role="status"
      aria-live="polite"
      aria-label={`Interview state: ${config.text}`}
    >
      <div className={`flex items-center gap-2 md:gap-3 ${config.textColor}`}>
        <div className="shrink-0">{config.icon}</div>
        <p className="font-semibold text-xs sm:text-sm md:text-base">{config.text}</p>
        {state === 'candidate_speaking' && (
          <div className="ml-auto shrink-0">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
