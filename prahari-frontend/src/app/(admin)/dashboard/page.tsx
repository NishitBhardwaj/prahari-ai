"use client"

import { KPIBar } from "@/components/analytics/KPIBar"
import { CrimeTrendChart } from "@/components/analytics/CrimeTrendChart"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { useUIStore } from "@/lib/stores/ui.store"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ShieldAlert, Activity } from "lucide-react"
import { cn } from "@/lib/utils"

export default function ExecutiveDashboard() {
  const { presentationMode, demoActive } = useUIStore()

  return (
    <div className={cn(
      "space-y-6 transition-all duration-500",
      presentationMode ? "p-4" : "p-0"
    )}>
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-heading text-primary dark:text-accent">
            Executive Command Center
          </h1>
          <p className="text-muted-foreground">
            State-wide intelligence overview and high-priority case alerts.
          </p>
        </div>
      </div>

      {demoActive && (
        <Alert variant="destructive" className="animate-in slide-in-from-top-4 fade-in duration-500 border-red-500/50 bg-red-500/10">
          <ShieldAlert className="h-5 w-5" />
          <AlertTitle className="text-lg font-bold">Priority 1 Incident Detected: Armed Robbery (Bengaluru South)</AlertTitle>
          <AlertDescription className="text-base mt-1">
            <span className="font-semibold">Suspects:</span> 3 unidentified males, armed with firearms.
            <br />
            <span className="font-semibold">AI Prediction:</span> 85% probability linked to 'Bawariya Gang' (recidivism detected).
            <br />
            <span className="font-semibold">Action:</span> FIR automatically drafted. Case assigned to ACP South.
          </AlertDescription>
        </Alert>
      )}

      <KPIBar />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4 bg-card border-border shadow-md">
          <CardHeader>
            <CardTitle>Crime Volume Trends</CardTitle>
            <CardDescription>
              Year-over-year comparison of major crime categories across Karnataka.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CrimeTrendChart />
          </CardContent>
        </Card>
        
        <Card className="col-span-3 bg-card border-border shadow-md">
          <CardHeader>
            <CardTitle>AI Risk Radar</CardTitle>
            <CardDescription>
              Predictive alerts based on temporal and geospatial anomaly detection.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Placeholder for AI Risk anomalies list */}
            {[
              { region: "Mysuru Central", risk: "High", reason: "Sudden spike in vehicle thefts (14 in 48hrs).", color: "text-red-500", bg: "bg-red-500/10" },
              { region: "Mangaluru Port", risk: "Medium", reason: "Unusual financial transaction clusters identified.", color: "text-amber-500", bg: "bg-amber-500/10" },
              { region: "Hubli-Dharwad", risk: "Medium", reason: "Historical pattern suggests imminent gang dispute.", color: "text-amber-500", bg: "bg-amber-500/10" },
            ].map((alert, i) => (
              <div key={i} className={`flex items-start gap-4 rounded-lg border border-border p-4 ${alert.bg}`}>
                <Activity className={`mt-0.5 h-5 w-5 ${alert.color}`} />
                <div className="space-y-1">
                  <p className="text-sm font-medium leading-none">{alert.region}</p>
                  <p className="text-sm text-muted-foreground">{alert.reason}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
