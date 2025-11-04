/**
 * Video Grid Layout Component
 * 
 * Google Meet-style grid layout for video interview
 * - With self-view: AI tile (60%) + candidate tile (40%) side-by-side
 * - Without self-view: AI tile (100% width)
 * - Controls always at bottom spanning full width
 */

import { ReactNode } from 'react'

export interface VideoGridLayoutProps {
  children: ReactNode
  className?: string
  selfViewVisible?: boolean
}

export function VideoGridLayout({ children, className = '', selfViewVisible = true }: VideoGridLayoutProps) {
  return (
    <main 
      className={`
        grid h-screen w-screen bg-background overflow-hidden
        ${selfViewVisible 
          ? 'md:grid-cols-[60%_1fr] md:grid-rows-[1fr_auto] md:gap-3 md:p-3 lg:gap-4 lg:p-4' 
          : 'grid-cols-1 grid-rows-[1fr_auto] gap-4 p-4'
        }
        ${className}
      `}
      style={{
        gridTemplateAreas: selfViewVisible 
          ? `
            "ai-tile candidate-tile"
            "controls controls"
          `
          : '"ai-tile" "controls"'
      }}
      role="main"
      aria-label={selfViewVisible ? "Video Interview Layout" : "Full Screen Interview Layout"}
    >
      {children}
    </main>
  )
}
