"use client"

import { useEffect, useRef } from "react"
import { cn } from "@/lib/utils"

interface WaveformVisualizerProps {
  isActive: boolean
  className?: string
}

export function WaveformVisualizer({ isActive, className }: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!isActive || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationId: number
    let phase = 0

    const draw = () => {
      const width = canvas.width
      const height = canvas.height
      const centerY = height / 2

      ctx.clearRect(0, 0, width, height)
      ctx.beginPath()
      ctx.strokeStyle = "#A16AE8"
      ctx.lineWidth = 2

      for (let x = 0; x < width; x++) {
        const y = centerY + Math.sin((x + phase) * 0.05) * (height * 0.3) * Math.random()
        if (x === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }

      ctx.stroke()
      phase += 2
      animationId = requestAnimationFrame(draw)
    }

    draw()

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [isActive])

  return <canvas ref={canvasRef} width={300} height={80} className={cn("w-full h-20", className)} />
}
