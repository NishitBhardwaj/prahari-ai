"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"

export default function CyberIntelligencePage() {
  const { presentationMode } = useUIStore()

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-4"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Cyber Intelligence
          </h1>
          <p className="text-muted-foreground">
            Digital footprints, fraud typologies, and device analytics.
          </p>
        </div>
      )}
      
      <div className="flex-1 w-full bg-card rounded-lg border border-border shadow-md flex items-center justify-center">
        <p className="text-muted-foreground">Cybercrime trends and typologies visualization would render here.</p>
      </div>
    </div>
  )
}
