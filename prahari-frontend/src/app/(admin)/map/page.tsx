"use client"

import { CrimeMap } from "@/components/map/CrimeMap"
import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"

export default function MapPage() {
  const { presentationMode } = useUIStore()

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-0"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Geospatial Intelligence
          </h1>
          <p className="text-muted-foreground">
            Live hotspot mapping and AI-driven spatial risk analysis across Karnataka.
          </p>
        </div>
      )}
      
      <div className="flex-1 w-full relative">
        <CrimeMap />
      </div>
    </div>
  )
}
