"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

export default function PredictiveIntelligencePage() {
  const { presentationMode } = useUIStore()

  return (
    <div className={cn(
      "flex flex-col h-[calc(100vh-8rem)] w-full transition-all duration-500",
      presentationMode ? "p-0 h-[calc(100vh-4rem)]" : "p-4"
    )}>
      {!presentationMode && (
        <div className="mb-4">
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Predictive Intelligence
          </h1>
          <p className="text-muted-foreground">
            AI risk scoring, anomaly detection, and explainable AI insights.
          </p>
        </div>
      )}
      
      <div className="grid gap-6 md:grid-cols-2 flex-1 w-full">
        <Card className="bg-card border-border shadow-md">
          <CardHeader>
            <CardTitle>Feature Importance (Risk Score: 85%)</CardTitle>
            <CardDescription>Why did the AI flag CASE-DEMO-001 as gang-related?</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              <li className="flex items-center justify-between">
                <span>Modus Operandi Match (Bawariya)</span>
                <span className="font-bold text-red-500">High Impact</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Geospatial Proximity to prior hits</span>
                <span className="font-bold text-amber-500">Medium Impact</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Time of Day (2:00 AM - 4:00 AM)</span>
                <span className="font-bold text-amber-500">Medium Impact</span>
              </li>
            </ul>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border shadow-md flex items-center justify-center">
          <p className="text-muted-foreground">Anomaly detection chart would render here.</p>
        </Card>
      </div>
    </div>
  )
}
