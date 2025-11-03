/**
 * Caption Display Tests
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { CaptionDisplay } from './CaptionDisplay'
import { describe, it, expect, vi } from 'vitest'

describe('CaptionDisplay', () => {
  it('renders caption text when visible', () => {
    render(
      <CaptionDisplay
        text="Hello, how are you?"
        isVisible={true}
        enabled={true}
        onToggleEnabled={() => {}}
      />
    )
    
    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
  })

  it('does not render when disabled', () => {
    const { container } = render(
      <CaptionDisplay
        text="Hello"
        isVisible={true}
        enabled={false}
        onToggleEnabled={() => {}}
      />
    )
    
    expect(container.firstChild).toBeNull()
  })

  it('applies visibility classes correctly', () => {
    const { rerender } = render(
      <CaptionDisplay
        text="Test"
        isVisible={true}
        enabled={true}
        onToggleEnabled={() => {}}
      />
    )
    
    let captionText = screen.getByText('Test')
    // After Tailwind refactoring, check for opacity-100 instead of 'visible' class
    expect(captionText).toHaveClass('opacity-100')
    
    rerender(
      <CaptionDisplay
        text="Test"
        isVisible={false}
        enabled={true}
        onToggleEnabled={() => {}}
      />
    )
    
    captionText = screen.getByText('Test')
    expect(captionText).toHaveClass('opacity-0')
  })

  it('calls onToggleEnabled when toggle button clicked', () => {
    const handleToggle = vi.fn()
    
    render(
      <CaptionDisplay
        text="Test"
        isVisible={true}
        enabled={true}
        onToggleEnabled={handleToggle}
      />
    )
    
    const toggleButton = screen.getByRole('button', { name: /disable captions/i })
    fireEvent.click(toggleButton)
    
    expect(handleToggle).toHaveBeenCalledTimes(1)
  })

  it('has correct ARIA attributes', () => {
    render(
      <CaptionDisplay
        text="Test"
        isVisible={true}
        enabled={true}
        onToggleEnabled={() => {}}
      />
    )
    
    const region = screen.getByRole('region')
    expect(region).toHaveAttribute('aria-label', 'AI Captions')
    expect(region).toHaveAttribute('aria-live', 'polite')
  })
})
