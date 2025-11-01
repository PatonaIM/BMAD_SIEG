import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PushToTalkButton } from './PushToTalkButton';

describe('PushToTalkButton', () => {
  it('renders in idle state', () => {
    render(<PushToTalkButton state="idle" />);
    expect(screen.getByText(/hold to speak/i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('shows recording state with pulsing red button', () => {
    render(<PushToTalkButton state="recording" />);
    expect(screen.getByText(/release to submit/i)).toBeInTheDocument();
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-red-500');
    expect(button).toHaveClass('animate-pulse');
  });

  it('shows processing state with spinner', () => {
    render(<PushToTalkButton state="processing" />);
    expect(screen.getByText(/processing/i)).toBeInTheDocument();
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('shows error state with error message', () => {
    const errorMessage = 'Microphone access denied';
    render(<PushToTalkButton state="error" error={errorMessage} />);
    const messages = screen.getAllByText(errorMessage);
    expect(messages).toHaveLength(2); // Button label and error message below
  });

  it('calls onMouseDown when mouse button pressed in idle state', () => {
    const handleMouseDown = vi.fn();
    render(<PushToTalkButton state="idle" onMouseDown={handleMouseDown} />);
    
    const button = screen.getByRole('button');
    fireEvent.mouseDown(button);
    
    expect(handleMouseDown).toHaveBeenCalledTimes(1);
  });

  it('calls onMouseUp when mouse button released in recording state', () => {
    const handleMouseUp = vi.fn();
    render(<PushToTalkButton state="recording" onMouseUp={handleMouseUp} />);
    
    const button = screen.getByRole('button');
    fireEvent.mouseUp(button);
    
    expect(handleMouseUp).toHaveBeenCalledTimes(1);
  });

  it('does not call onMouseDown when button is disabled', () => {
    const handleMouseDown = vi.fn();
    render(
      <PushToTalkButton 
        state="idle" 
        onMouseDown={handleMouseDown} 
        disabled={true} 
      />
    );
    
    const button = screen.getByRole('button');
    fireEvent.mouseDown(button);
    
    expect(handleMouseDown).not.toHaveBeenCalled();
  });

  it('prevents recording when already recording (double-click prevention)', () => {
    const handleMouseDown = vi.fn();
    render(<PushToTalkButton state="recording" onMouseDown={handleMouseDown} />);
    
    const button = screen.getByRole('button');
    fireEvent.mouseDown(button);
    
    expect(handleMouseDown).not.toHaveBeenCalled();
  });

  it('supports touch events for mobile devices', () => {
    const handleTouchStart = vi.fn();
    const handleTouchEnd = vi.fn();
    
    render(
      <PushToTalkButton 
        state="idle" 
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      />
    );
    
    const button = screen.getByRole('button');
    fireEvent.touchStart(button);
    fireEvent.touchEnd(button);
    
    expect(handleTouchStart).toHaveBeenCalledTimes(1);
    expect(handleTouchEnd).toHaveBeenCalledTimes(1);
  });

  it('has correct aria attributes for accessibility', () => {
    render(<PushToTalkButton state="idle" />);
    const button = screen.getByRole('button');
    
    expect(button).toHaveAttribute('aria-label', 'Hold to Speak');
    expect(button).toHaveAttribute('aria-pressed', 'false');
  });

  it('updates aria-pressed when recording', () => {
    render(<PushToTalkButton state="recording" />);
    const button = screen.getByRole('button');
    
    expect(button).toHaveAttribute('aria-pressed', 'true');
  });
});
