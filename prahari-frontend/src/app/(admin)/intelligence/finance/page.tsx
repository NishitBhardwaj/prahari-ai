"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"
import ReactECharts from "echarts-for-react"
import { useTheme } from "next-themes"

export default function FinancialIntelligencePage() {
  const { presentationMode } = useUIStore()
  const { theme } = useTheme()

  const sankeyOption = {
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [
      {
        type: 'sankey',
        data: [
          { name: 'Victim A (UPI)' },
          { name: 'Victim B (UPI)' },
          { name: 'Mule Account 1' },
          { name: 'Mule Account 2' },
          { name: 'Crypto Exchange' },
          { name: 'Overseas Withdrawal' }
        ],
        links: [
          { source: 'Victim A (UPI)', target: 'Mule Account 1', value: 50000 },
          { source: 'Victim B (UPI)', target: 'Mule Account 1', value: 25000 },
          { source: 'Victim B (UPI)', target: 'Mule Account 2', value: 15000 },
          { source: 'Mule Account 1', target: 'Crypto Exchange', value: 75000 },
          { source: 'Mule Account 2', target: 'Crypto Exchange', value: 15000 },
          { source: 'Crypto Exchange', target: 'Overseas Withdrawal', value: 90000 },
        ],
        label: {
          color: theme === 'dark' ? '#cbd5e1' : '#334155',
        },
        itemStyle: {
          borderWidth: 1,
          borderColor: '#1e293b'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.5
        }
      }
    ]
  };

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-4"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Financial Intelligence
          </h1>
          <p className="text-muted-foreground">
            Follow the money: Cyber fraud flows and Hawala money laundering networks.
          </p>
        </div>
      )}
      
      <div className="flex-1 w-full bg-card rounded-lg border border-border shadow-md p-4">
        <h3 className="font-heading font-bold mb-4">Fraud Flow Sankey Analysis</h3>
        <div className="h-[calc(100%-3rem)] w-full">
          <ReactECharts 
            option={sankeyOption} 
            style={{ height: '100%', width: '100%' }}
            theme={theme === 'dark' ? 'dark' : 'light'}
          />
        </div>
      </div>
    </div>
  )
}
