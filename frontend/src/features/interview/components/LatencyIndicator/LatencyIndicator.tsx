/**
 * Latency Indicator Component
 * 
 * Displays connection latency with color-coded feedback
 * Auto-hides after stable connection
 */

import { useEffect, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Activity } from 'lucide-react'

export interface LatencyIndicatorProps {
  latency: number | null
  className?: string
  autoHideDelay?: number
}

interface LatencyStats {
  current: number | null
  average: number | null
  measurements: number[]
}

/**
 * Get latency status configuration
 */
function getLatencyStatus(latency: number | null) {
  if (latency === null) {
    return {
      label: 'Connecting...',
      variant: 'outline' as const,
      color: 'text-muted-foreground',
      description: 'Establishing connection'
    }
  }
  
  if (latency < 500) {
    return {
      label: `${latency}ms`,
      variant: 'default' as const,
      color: 'text-green-600',
      description: 'Excellent connection'
    }
  }
  
  if (latency < 1000) {
    return {
      label: `${latency}ms`,
      variant: 'secondary' as const,
      color: 'text-yellow-600',
      description: 'Good connection'
    }
  }
  
  return {
    label: `${latency}ms`,
    variant: 'destructive' as const,
    color: 'text-red-600',
    description: 'Poor connection - May affect quality'
  }
}

/**
 * Latency Indicator Component
 * 
 * Displays real-time connection latency with visual feedback
 * Auto-hides after stable connection to reduce UI clutter
 */
export function LatencyIndicator({ 
  latency, 
  className = '',
  autoHideDelay = 3000
}: LatencyIndicatorProps) {
  const [stats, setStats] = useState<LatencyStats>({
    current: null,
    average: null,
    measurements: []
  })
  const [isVisible, setIsVisible] = useState(true)
  const [hideTimeout, setHideTimeout] = useState<NodeJS.Timeout | null>(null)

  // Track latency measurements
  useEffect(() => {
    if (latency !== null) {
      setStats(prev => {
        const newMeasurements = [...prev.measurements, latency].slice(-10) // Keep last 10
        const average = Math.round(
          newMeasurements.reduce((sum, val) => sum + val, 0) / newMeasurements.length
        )
        
        return {
          current: latency,
          average,
          measurements: newMeasurements
        }
      })
      
      // Show indicator when new measurement arrives
      setIsVisible(true)
      
      // Clear existing timeout
      if (hideTimeout) {
        clearTimeout(hideTimeout)
      }
      
      // Set new auto-hide timeout
      const timeout = setTimeout(() => {
        setIsVisible(false)
      }, autoHideDelay)
      
      setHideTimeout(timeout)
    }
  }, [latency, autoHideDelay])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hideTimeout) {
        clearTimeout(hideTimeout)
      }
    }
  }, [hideTimeout])

  const status = getLatencyStatus(stats.current)

  if (!isVisible) {
    return null
  }

  return (
    <div
      className={`
        fixed top-4 right-4 z-50
        flex flex-col gap-1
        transition-all duration-300
        ${className}
      `}
      role="status"
      aria-live="polite"
      aria-label={`Connection latency: ${status.description}`}
    >
      <Badge 
        variant={status.variant}
        className="flex items-center gap-2 shadow-lg"
      >
        <Activity className={`w-3 h-3 ${status.color}`} />
        <span className="font-mono text-xs">{status.label}</span>
      </Badge>
      
      {stats.average !== null && stats.measurements.length > 1 && (
        <div className="text-xs text-muted-foreground text-right bg-background/80 px-2 py-1 rounded-md shadow-md">
          Avg: <span className="font-mono">{stats.average}ms</span>
        </div>
      )}
      
      {stats.current !== null && stats.current >= 1000 && (
        <div className="text-xs text-destructive text-right bg-background/80 px-2 py-1 rounded-md shadow-md">
          ⚠️ High latency detected
        </div>
      )}
    </div>
  )
}
