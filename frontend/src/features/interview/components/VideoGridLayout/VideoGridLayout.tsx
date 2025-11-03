/**
 * Video Grid Layout Component
 * 
 * Google Meet-style grid layout for video interview
 * - Desktop: AI tile (60%) + candidate tile (30%) side-by-side
 * - Tablet: Same grid scaled down
 * - Mobile: AI full-screen + candidate floating overlay
 * - Audio-only: AI tile centered, candidate tile hidden
 */

import { ReactNode } from 'react'

export interface VideoGridLayoutProps {
  children: ReactNode
  className?: string
  audioOnlyMode?: boolean
}

export function VideoGridLayout({ children, className = '', audioOnlyMode = false }: VideoGridLayoutProps) {
  return (
    <main 
      className={`
        grid h-screen w-screen bg-background overflow-hidden
        ${audioOnlyMode 
          ? 'grid-cols-1 grid-rows-[1fr_auto] gap-4 p-4' 
          : 'md:grid-cols-[65%_1fr] md:grid-rows-[1fr_auto] md:gap-3 md:p-3 lg:grid-cols-[60%_1fr] lg:gap-4 lg:p-4'
        }
        ${className}
      `}
      style={{
        gridTemplateAreas: audioOnlyMode 
          ? '"ai-tile" "controls"'
          : `
            "ai-tile candidate-tile"
            "ai-tile controls"
          `
      }}
      role="main"
      aria-label={audioOnlyMode ? "Audio-Only Interview Layout" : "Video Interview Layout"}
    >
      {children}
    </main>
  )
}
