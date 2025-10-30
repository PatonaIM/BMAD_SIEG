export interface ProgressIndicatorProps {
  value: number
  max?: number
}

export function ProgressIndicator({ value, max = 100 }: ProgressIndicatorProps) {
  return <div>{`${value}/${max}`}</div>
}
