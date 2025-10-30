export interface WaveformVisualizerProps {
  audioLevel: number
  isActive: boolean
  barCount?: number
}

export function WaveformVisualizer({ audioLevel, isActive, barCount = 25 }: WaveformVisualizerProps) {
  return <canvas width={300} height={100} />
}
