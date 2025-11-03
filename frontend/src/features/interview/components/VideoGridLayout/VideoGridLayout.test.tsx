/**
 * Video Grid Layout Tests
 */

import { render, screen } from '@testing-library/react'
import { VideoGridLayout } from './VideoGridLayout'
import { describe, it, expect } from 'vitest'

describe('VideoGridLayout', () => {
  it('renders children correctly', () => {
    render(
      <VideoGridLayout>
        <div data-testid="ai-tile">AI</div>
        <div data-testid="candidate-tile">Candidate</div>
        <div data-testid="controls">Controls</div>
      </VideoGridLayout>
    )
    
    expect(screen.getByTestId('ai-tile')).toBeInTheDocument()
    expect(screen.getByTestId('candidate-tile')).toBeInTheDocument()
    expect(screen.getByTestId('controls')).toBeInTheDocument()
  })

  it('has correct ARIA label', () => {
    render(<VideoGridLayout><div>Content</div></VideoGridLayout>)
    
    const layout = screen.getByRole('main')
    expect(layout).toHaveAttribute('aria-label', 'Video Interview Layout')
  })

  it('applies custom className', () => {
    render(
      <VideoGridLayout className="custom-class">
        <div>Child content</div>
      </VideoGridLayout>
    )
    
    const layout = screen.getByRole('main')
    // After Tailwind refactoring, we check for grid class instead of CSS class
    expect(layout).toHaveClass('grid')
    expect(layout).toHaveClass('custom-class')
  })
})
