/**
 * AI Presence Orb Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AIPresenceOrb } from './AIPresenceOrb'

describe('AIPresenceOrb', () => {
  it('renders idle state with pulsing animation', () => {
    render(<AIPresenceOrb state="idle" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*idle/i })
    expect(orb).toBeInTheDocument()
  })

  it('renders listening state with ripple animation', () => {
    render(<AIPresenceOrb state="listening" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*listening/i })
    expect(orb).toBeInTheDocument()
    
    // Check for ripple elements
    const orbCore = orb.querySelector('.orb-core')
    expect(orbCore).toHaveClass('state-listening')
  })

  it('renders thinking state with circular progress', () => {
    render(<AIPresenceOrb state="thinking" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*thinking/i })
    expect(orb).toBeInTheDocument()
    
    // Check for thinking spinner SVG
    const orbCore = orb.querySelector('.orb-core')
    expect(orbCore).toHaveClass('state-thinking')
  })

  it('renders speaking state with waveform canvas', () => {
    render(<AIPresenceOrb state="speaking" audioLevel={0.5} />)
    const orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    expect(orb).toBeInTheDocument()
    
    // Check for canvas element
    const canvas = orb.querySelector('canvas')
    expect(canvas).toBeInTheDocument()
    expect(canvas).toHaveClass('waveform-canvas')
  })

  it('updates waveform when audioLevel changes', () => {
    const { rerender } = render(<AIPresenceOrb state="speaking" audioLevel={0.3} />)
    const orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    const canvas = orb.querySelector('canvas')
    expect(canvas).toBeInTheDocument()

    // Rerender with different audio level
    rerender(<AIPresenceOrb state="speaking" audioLevel={0.8} />)
    expect(canvas).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<AIPresenceOrb state="idle" className="custom-class" />)
    const orb = screen.getByRole('img', { name: /AI Presence/i })
    expect(orb).toHaveClass('custom-class')
  })

  it('renders small size variant', () => {
    render(<AIPresenceOrb state="idle" size="sm" />)
    const orb = screen.getByRole('img', { name: /AI Presence/i })
    expect(orb).toHaveStyle({ width: '150px', height: '150px' })
  })

  it('renders medium size variant (default)', () => {
    render(<AIPresenceOrb state="idle" size="md" />)
    const orb = screen.getByRole('img', { name: /AI Presence/i })
    expect(orb).toHaveStyle({ width: '200px', height: '200px' })
  })

  it('renders large size variant', () => {
    render(<AIPresenceOrb state="idle" size="lg" />)
    const orb = screen.getByRole('img', { name: /AI Presence/i })
    expect(orb).toHaveStyle({ width: '300px', height: '300px' })
  })

  it('has proper accessibility attributes', () => {
    render(<AIPresenceOrb state="listening" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*listening/i })
    expect(orb).toHaveAttribute('role', 'img')
    expect(orb).toHaveAttribute('aria-label')
  })

  it('transitions between states smoothly', () => {
    const { rerender } = render(<AIPresenceOrb state="idle" />)
    let orb = screen.getByRole('img', { name: /AI Presence.*idle/i })
    expect(orb).toBeInTheDocument()

    // Transition to listening
    rerender(<AIPresenceOrb state="listening" />)
    orb = screen.getByRole('img', { name: /AI Presence.*listening/i })
    expect(orb).toBeInTheDocument()

    // Transition to thinking
    rerender(<AIPresenceOrb state="thinking" />)
    orb = screen.getByRole('img', { name: /AI Presence.*thinking/i })
    expect(orb).toBeInTheDocument()

    // Transition to speaking
    rerender(<AIPresenceOrb state="speaking" audioLevel={0.5} />)
    orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    expect(orb).toBeInTheDocument()
  })

  it('defaults audioLevel to 0 if not provided', () => {
    render(<AIPresenceOrb state="speaking" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    expect(orb).toBeInTheDocument()
  })

  it('handles audioLevel at boundary values', () => {
    const { rerender } = render(<AIPresenceOrb state="speaking" audioLevel={0} />)
    let orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    expect(orb).toBeInTheDocument()

    rerender(<AIPresenceOrb state="speaking" audioLevel={1} />)
    orb = screen.getByRole('img', { name: /AI Presence.*speaking/i })
    expect(orb).toBeInTheDocument()
  })

  it('renders idle state elements correctly', () => {
    render(<AIPresenceOrb state="idle" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*idle/i })
    
    const orbCore = orb.querySelector('.orb-core')
    expect(orbCore).toHaveClass('state-idle')
    
    const pulseRing = orb.querySelector('.pulse-ring')
    expect(pulseRing).toBeInTheDocument()
  })

  it('renders listening state elements correctly', () => {
    render(<AIPresenceOrb state="listening" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*listening/i })
    
    const orbCore = orb.querySelector('.orb-core')
    expect(orbCore).toHaveClass('state-listening')
    
    // Check for all ripple elements
    const ripples = orb.querySelectorAll('.ripple')
    expect(ripples.length).toBe(3)
  })

  it('renders thinking state elements correctly', () => {
    render(<AIPresenceOrb state="thinking" />)
    const orb = screen.getByRole('img', { name: /AI Presence.*thinking/i })
    
    const orbCore = orb.querySelector('.orb-core')
    expect(orbCore).toHaveClass('state-thinking')
    
    // Check for spinner SVG
    const spinner = orb.querySelector('.thinking-spinner')
    expect(spinner).toBeInTheDocument()
    
    // Check for SVG circle
    const circle = orb.querySelector('circle')
    expect(circle).toBeInTheDocument()
  })
})
