/**
 * AI Presence Orb Component
 * 
 * Animated visual representation of AI interviewer state
 * Displays different animations for idle, listening, thinking, and speaking states
 * Syncs with audio levels during speaking state
 */

import { useEffect, useState, useRef } from 'react'
import './AIPresenceOrb.css'

export type OrbState = 'idle' | 'listening' | 'thinking' | 'speaking'

export interface AIPresenceOrbProps {
  state: OrbState
  audioLevel?: number // 0.0 to 1.0, used in 'speaking' state
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

const SIZE_MAP = {
  sm: 150,
  md: 200,
  lg: 300,
}

/**
 * AI Presence Orb Component
 * 
 * Renders animated orb with state-based animations
 * - Idle: Subtle pulsing
 * - Listening: Ripple effect
 * - Thinking: Circular progress
 * - Speaking: Audio waveform visualization
 */
export function AIPresenceOrb({ 
  state, 
  audioLevel = 0, 
  className = '',
  size = 'md' 
}: AIPresenceOrbProps) {
  const [showStaticOrb, setShowStaticOrb] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationFrameRef = useRef<number | undefined>(undefined)
  const fpsCountRef = useRef(0)
  const lowFpsFramesRef = useRef(0)
  const lastFrameTimeRef = useRef(Date.now())
  const thinkingRotationRef = useRef(0)
  const waveformBarsRef = useRef<number[]>(new Array(12).fill(0.2))
  
  const orbSize = SIZE_MAP[size]

  // Performance monitoring and fallback logic
  useEffect(() => {
    const monitorPerformance = () => {
      const now = Date.now()
      const delta = now - lastFrameTimeRef.current
      const fps = 1000 / delta
      
      lastFrameTimeRef.current = now
      
      if (fps < 24) {
        lowFpsFramesRef.current++
        if (lowFpsFramesRef.current > 180) { // 3 seconds at 60fps
          setShowStaticOrb(true)
        }
      } else {
        lowFpsFramesRef.current = Math.max(0, lowFpsFramesRef.current - 1)
      }
    }

    const interval = setInterval(monitorPerformance, 1000)
    return () => clearInterval(interval)
  }, [])

  // Canvas animation for speaking state
  useEffect(() => {
    if (state !== 'speaking' || showStaticOrb) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      return
    }

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2
    const radius = orbSize / 2

    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Update waveform bars with smooth interpolation
      const targetHeight = 0.2 + audioLevel * 0.6
      waveformBarsRef.current = waveformBarsRef.current.map(bar => {
        const diff = targetHeight - bar
        return bar + diff * 0.15 // Smooth interpolation
      })

      // Rotate bars for visual interest
      waveformBarsRef.current.push(waveformBarsRef.current.shift()!)

      // Draw waveform bars in circular arrangement
      const barCount = 12
      const angleStep = (Math.PI * 2) / barCount
      
      waveformBarsRef.current.forEach((barHeight, i) => {
        const angle = i * angleStep - Math.PI / 2
        const barRadius = radius * 0.7
        const barLength = radius * 0.3 * barHeight
        
        const startX = centerX + Math.cos(angle) * barRadius
        const startY = centerY + Math.sin(angle) * barRadius
        const endX = centerX + Math.cos(angle) * (barRadius + barLength)
        const endY = centerY + Math.sin(angle) * (barRadius + barLength)

        ctx.beginPath()
        ctx.moveTo(startX, startY)
        ctx.lineTo(endX, endY)
        ctx.strokeStyle = 'var(--primary)'
        ctx.lineWidth = 4
        ctx.lineCap = 'round'
        ctx.stroke()
      })

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [state, audioLevel, orbSize, showStaticOrb])

  // Fallback to static logo
  if (showStaticOrb) {
    return (
      <div 
        className={`ai-presence-orb static ${className}`}
        style={{ width: orbSize, height: orbSize }}
        role="img"
        aria-label="AI Presence (Static)"
      >
        <div className="orb-core static" />
      </div>
    )
  }

  return (
    <div 
      className={`ai-presence-orb ${className}`}
      style={{ width: orbSize, height: orbSize }}
      role="img"
      aria-label={`AI Presence - ${state}`}
    >
      {/* Main orb with gradient */}
      <div className={`orb-core state-${state}`}>
        {/* Idle state: pulsing animation (CSS) */}
        {state === 'idle' && (
          <div className="pulse-ring" />
        )}

        {/* Listening state: ripple effect */}
        {state === 'listening' && (
          <>
            <div className="ripple ripple-1" />
            <div className="ripple ripple-2" />
            <div className="ripple ripple-3" />
          </>
        )}

        {/* Thinking state: circular progress */}
        {state === 'thinking' && (
          <svg className="thinking-spinner" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="var(--accent)"
              strokeWidth="4"
              strokeDasharray="251.2"
              strokeDashoffset="62.8"
              strokeLinecap="round"
            />
          </svg>
        )}

        {/* Speaking state: waveform visualization (Canvas) */}
        {state === 'speaking' && (
          <canvas
            ref={canvasRef}
            width={orbSize}
            height={orbSize}
            className="waveform-canvas"
          />
        )}
      </div>
    </div>
  )
}
