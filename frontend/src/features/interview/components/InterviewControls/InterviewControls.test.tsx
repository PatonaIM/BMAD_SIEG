/**
 * Interview Controls Tests
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { InterviewControls } from './InterviewControls'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('InterviewControls', () => {
  const mockHandlers = {
    onToggleMute: vi.fn(),
    onToggleCamera: vi.fn(),
    onEndInterview: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders all control buttons', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    expect(screen.getByRole('button', { name: /mute microphone/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /turn camera off/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /end interview/i })).toBeInTheDocument()
  })

  it('shows correct mute button state', () => {
    const { rerender } = render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    expect(screen.getByRole('button', { name: /mute microphone/i })).toBeInTheDocument()
    
    rerender(
      <InterviewControls
        isMuted={true}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    expect(screen.getByRole('button', { name: /unmute microphone/i })).toBeInTheDocument()
  })

  it('calls onToggleMute when mute button clicked', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    const muteButton = screen.getByRole('button', { name: /mute microphone/i })
    fireEvent.click(muteButton)
    
    expect(mockHandlers.onToggleMute).toHaveBeenCalledTimes(1)
  })

  it('calls onToggleCamera when camera button clicked', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    const cameraButton = screen.getByRole('button', { name: /turn camera off/i })
    fireEvent.click(cameraButton)
    
    expect(mockHandlers.onToggleCamera).toHaveBeenCalledTimes(1)
  })

  it('calls onEndInterview when end button clicked', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    const endButton = screen.getByRole('button', { name: /end interview/i })
    fireEvent.click(endButton)
    
    expect(mockHandlers.onEndInterview).toHaveBeenCalledTimes(1)
  })

  it('triggers onToggleMute on Space keypress', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    fireEvent.keyDown(document, { code: 'Space' })
    
    expect(mockHandlers.onToggleMute).toHaveBeenCalledTimes(1)
  })

  it('triggers onToggleCamera on V keypress', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    fireEvent.keyDown(document, { code: 'KeyV' })
    
    expect(mockHandlers.onToggleCamera).toHaveBeenCalledTimes(1)
  })

  it('has correct ARIA attributes', () => {
    render(
      <InterviewControls
        isMuted={false}
        isCameraOn={true}
        {...mockHandlers}
      />
    )
    
    const toolbar = screen.getByRole('toolbar')
    expect(toolbar).toHaveAttribute('aria-label', 'Interview Controls')
  })
})
