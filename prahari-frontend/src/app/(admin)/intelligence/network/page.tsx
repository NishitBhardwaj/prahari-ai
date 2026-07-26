"use client"

import { NetworkVisualizer } from "@/components/graph/NetworkVisualizer"
import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"

export default function NetworkIntelligencePage() {
  const { presentationMode } = useUIStore()

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-0"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Criminal Network Intelligence
          </h1>
          <p className="text-muted-foreground">
            Explore syndicates, communication links, and entity relationships via Neo4j Graph.
          </p>
        </div>
      )}
      
      <div className="flex-1 w-full relative">
        <NetworkVisualizer />
        
        {/* Overlay Filters */}
        <div className="absolute top-4 left-4 z-10 bg-card/90 backdrop-blur-sm p-4 rounded-lg shadow-lg border border-border w-64">
          <h3 className="font-heading font-bold text-foreground">Graph Controls</h3>
          <p className="text-xs text-muted-foreground mb-4">Shortest Path Analysis</p>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span>Show Gangs</span>
              <input type="checkbox" defaultChecked className="rounded bg-background" />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Show Cases</span>
              <input type="checkbox" defaultChecked className="rounded bg-background" />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Show Evidence</span>
              <input type="checkbox" defaultChecked className="rounded bg-background" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
