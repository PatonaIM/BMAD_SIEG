import { Card } from '@/components/ui/card';
import { Headphones, Mic } from 'lucide-react';

export type InterviewState = 'ai_speaking' | 'ai_listening' | 'candidate_speaking' | 'processing';

export interface InterviewStateIndicatorProps {
  state: InterviewState;
  className?: string;
}

/**
 * Interview State Indicator Component
 * Displays whose turn it is to speak
 * Visual states: AI's turn or Your turn
 */
export function InterviewStateIndicator({ state, className = '' }: InterviewStateIndicatorProps) {
  const getStateConfig = () => {
    // Simplify: only show whose turn it is
    // AI's turn: ai_speaking, processing
    // Your turn: ai_listening, candidate_speaking
    const isAITurn = state === 'ai_speaking' || state === 'processing'
    
    if (isAITurn) {
      return {
        icon: <Headphones className="w-5 h-5" />,
        text: "AI's turn to speak",
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-500',
        textColor: 'text-purple-900',
      }
    } else {
      return {
        icon: <Mic className="w-5 h-5" />,
        text: 'Your turn to speak',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-500',
        textColor: 'text-blue-900',
      }
    }
  }

  const config = getStateConfig()

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
        ${className}
      `}
      role="status"
      aria-live="polite"
      aria-label={`Interview state: ${config.text}`}
    >
      <div className={`flex items-center gap-2 md:gap-3 ${config.textColor}`}>
        <div className="shrink-0">{config.icon}</div>
        <p className="font-semibold text-xs sm:text-sm md:text-base">{config.text}</p>
      </div>
    </Card>
  );
}
