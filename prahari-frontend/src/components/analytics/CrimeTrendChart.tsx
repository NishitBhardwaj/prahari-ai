"use client"

import ReactECharts from "echarts-for-react"
import { useTheme } from "next-themes"

export function CrimeTrendChart() {
  const { theme } = useTheme()

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['Theft', 'Violent Crime', 'Cyber Crime', 'Financial Fraud'],
      textStyle: {
        color: theme === 'dark' ? '#cbd5e1' : '#334155'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      axisLabel: {
        color: theme === 'dark' ? '#94a3b8' : '#64748b'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: theme === 'dark' ? '#94a3b8' : '#64748b'
      },
      splitLine: {
        lineStyle: {
          color: theme === 'dark' ? '#334155' : '#e2e8f0'
        }
      }
    },
    series: [
      {
        name: 'Theft',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210, 200, 180, 210, 240, 260],
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: 'Violent Crime',
        type: 'line',
        smooth: true,
        data: [22, 18, 19, 23, 29, 33, 31, 28, 25, 22, 21, 19],
        itemStyle: { color: '#ef4444' }
      },
      {
        name: 'Cyber Crime',
        type: 'line',
        smooth: true,
        data: [150, 232, 201, 154, 190, 330, 410, 450, 520, 580, 630, 710],
        itemStyle: { color: '#8b5cf6' }
      },
      {
        name: 'Financial Fraud',
        type: 'line',
        smooth: true,
        data: [80, 90, 95, 110, 105, 130, 150, 170, 160, 180, 200, 220],
        itemStyle: { color: '#f59e0b' }
      }
    ]
  };

  return (
    <div className="h-[400px] w-full">
      <ReactECharts 
        option={option} 
        style={{ height: '100%', width: '100%' }}
        theme={theme === 'dark' ? 'dark' : 'light'}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}
