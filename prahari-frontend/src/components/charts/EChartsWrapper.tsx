"use client"

import ReactECharts from "echarts-for-react"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"
import type { EChartsOption } from "echarts"

interface EChartsWrapperProps {
  option: EChartsOption;
  style?: React.CSSProperties;
  className?: string;
  onEvents?: Record<string, Function>;
}

export function EChartsWrapper({ option, style, className, onEvents }: EChartsWrapperProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch on theme
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div style={{ height: style?.height || '300px' }} className="flex items-center justify-center text-muted-foreground animate-pulse bg-secondary/50 rounded-lg" />
  }

  // Extend base options with our theme
  const mergedOption: EChartsOption = {
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: 'var(--font-inter), sans-serif',
    },
    tooltip: {
      backgroundColor: resolvedTheme === 'dark' ? '#1E293B' : '#ffffff',
      borderColor: resolvedTheme === 'dark' ? '#334155' : '#e2e8f0',
      textStyle: {
        color: resolvedTheme === 'dark' ? '#f8fafc' : '#0f172a'
      },
      ...((option.tooltip as any) || {})
    },
    ...option
  }

  return (
    <ReactECharts
      option={mergedOption}
      style={{ height: '100%', width: '100%', ...style }}
      className={className}
      theme={resolvedTheme === 'dark' ? 'dark' : 'light'}
      onEvents={onEvents}
      notMerge={true}
      lazyUpdate={true}
    />
  )
}
