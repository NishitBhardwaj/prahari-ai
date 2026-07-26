"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { Database, Server, Activity, Network, CheckCircle2 } from "lucide-react"
import { useEffect, useState } from "react"

export function SystemHealth() {
  const { presentationMode } = useUIStore()
  const [pulse, setPulse] = useState(false)

  useEffect(() => {
    if (presentationMode) {
      const interval = setInterval(() => setPulse(p => !p), 2000)
      return () => clearInterval(interval)
    }
  }, [presentationMode])

  if (!presentationMode) return null

  const metrics = [
    { name: 'PostgreSQL', icon: Database, value: 'Operational', latency: '4ms' },
    { name: 'Neo4j Graph', icon: Network, value: 'Synchronized', latency: '12ms' },
    { name: 'Qdrant Vector', icon: Server, value: 'Operational', latency: '8ms' },
    { name: 'Zoho Catalyst', icon: Activity, value: 'Connected', latency: '45ms' },
  ]

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-4 bg-card/90 backdrop-blur-md border border-border shadow-lg rounded-full px-6 py-2 animate-in slide-in-from-top-4">
      <div className="flex items-center gap-2 pr-4 border-r border-border">
        <div className="relative flex h-2 w-2">
          <span className={`absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 ${pulse ? 'animate-ping' : ''}`}></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </div>
        <span className="text-sm font-bold text-emerald-500 tracking-wider">SYSTEM HEALTH: NOMINAL</span>
      </div>
      
      {metrics.map((metric, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <metric.icon className="h-3 w-3 text-muted-foreground" />
          <span className="text-foreground">{metric.name}</span>
          <span className="text-muted-foreground opacity-50">•</span>
          <span className="text-emerald-500">{metric.latency}</span>
        </div>
      ))}
    </div>
  )
}
