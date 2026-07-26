"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"

export default function CommunicationIntelligencePage() {
  const { presentationMode } = useUIStore()

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-4"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Communication Intelligence
          </h1>
          <p className="text-muted-foreground">
            Call Detail Record (CDR) analysis and tower location link maps.
          </p>
        </div>
      )}
      
      <div className="flex-1 w-full bg-card rounded-lg border border-border shadow-md flex items-center justify-center">
        <p className="text-muted-foreground">CDR Link Analysis visualization would render here.</p>
      </div>
    </div>
  )
}
