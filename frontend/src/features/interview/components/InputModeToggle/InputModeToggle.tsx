import { useEffect } from 'react';
import { Mic, Keyboard } from 'lucide-react';

export type InputMode = 'voice' | 'text';

export interface InputModeToggleProps {
  mode: InputMode;
  onModeChange: (mode: InputMode) => void;
  className?: string;
}

/**
 * Input Mode Toggle Component
 * Allows switching between voice and text input modes
 * Persists preference to localStorage
 */
export function InputModeToggle({ mode, onModeChange, className = '' }: InputModeToggleProps) {
  // Load preference from localStorage on mount
  useEffect(() => {
    const savedMode = localStorage.getItem('interview_input_mode') as InputMode | null;
    if (savedMode && (savedMode === 'voice' || savedMode === 'text')) {
      onModeChange(savedMode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  const handleToggle = () => {
    const newMode: InputMode = mode === 'voice' ? 'text' : 'voice';
    onModeChange(newMode);
    localStorage.setItem('interview_input_mode', newMode);
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm text-gray-600">Input Mode:</span>
      <button
        type="button"
        onClick={handleToggle}
        className="relative inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all duration-200 hover:shadow-md"
        aria-label={`Switch to ${mode === 'voice' ? 'text' : 'voice'} mode`}
        title="Switch between voice and text input"
      >
        {/* Voice Mode */}
        <div
          className={`flex items-center gap-2 transition-all duration-200 ${
            mode === 'voice' ? 'text-purple-600 font-semibold' : 'text-gray-400'
          }`}
        >
          <Mic className="w-4 h-4" />
          <span className="text-sm">Voice</span>
        </div>

        {/* Divider */}
        <div className="h-4 w-px bg-gray-300" />

        {/* Text Mode */}
        <div
          className={`flex items-center gap-2 transition-all duration-200 ${
            mode === 'text' ? 'text-blue-600 font-semibold' : 'text-gray-400'
          }`}
        >
          <Keyboard className="w-4 h-4" />
          <span className="text-sm">Text</span>
        </div>

        {/* Active indicator */}
        <div
          className={`absolute bottom-0 h-1 bg-linear-to-r transition-all duration-200 ${
            mode === 'voice'
              ? 'left-0 w-1/2 from-purple-500 to-purple-600'
              : 'left-1/2 w-1/2 from-blue-500 to-blue-600'
          }`}
        />
      </button>

      <span className="text-xs text-gray-500 italic">
        {mode === 'voice' ? 'Hold button to speak' : 'Type your response'}
      </span>
    </div>
  );
}
