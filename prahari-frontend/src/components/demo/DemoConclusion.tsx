"use client"

import { useEffect, useState } from "react"
import { ShieldAlert, CheckCircle2, AlertTriangle, Activity, Database, Network } from "lucide-react"

export function DemoConclusion() {
  const [stage, setStage] = useState<'briefing' | 'showcase'>('briefing')

  // Automatically transition from Briefing to Showcase after 15 seconds
  useEffect(() => {
    if (stage === 'briefing') {
      const timer = setTimeout(() => {
        setStage('showcase')
      }, 15000)
      return () => clearTimeout(timer)
    }
  }, [stage])

  return (
    <div className="fixed inset-0 z-[100] bg-background/95 backdrop-blur-md flex flex-col items-center justify-center overflow-y-auto p-4 md:p-8 animate-in fade-in duration-1000">
      
      {stage === 'briefing' && (
        <div className="w-full max-w-4xl bg-card border border-border shadow-2xl rounded-2xl overflow-hidden animate-in slide-in-from-bottom-8 duration-700">
          <div className="bg-primary p-6 text-primary-foreground text-center">
            <h1 className="text-3xl font-heading font-bold">Executive Intelligence Summary</h1>
            <p className="opacity-90 mt-2">Automated Incident Report & Action Plan</p>
          </div>
          
          <div className="p-8 space-y-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <h3 className="text-xl font-semibold border-b border-border pb-2">Incident Details</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <span className="text-muted-foreground">Type:</span> <span className="font-medium">Gang Robbery</span>
                  <span className="text-muted-foreground">Location:</span> <span className="font-medium">Bengaluru Urban</span>
                  <span className="text-muted-foreground">Time:</span> <span className="font-medium">09:42 PM</span>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-xl font-semibold border-b border-border pb-2 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                  AI Assessment
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <span className="text-muted-foreground">Risk Score:</span> <span className="font-bold text-red-500">92%</span>
                  <span className="text-muted-foreground">Threat Level:</span> <span className="font-bold text-red-500">Critical</span>
                  <span className="text-muted-foreground">Predicted Repeat:</span> <span className="font-bold text-amber-500">High</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold border-b border-border pb-2">Investigation Progress</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {['FIR Generated', 'Evidence Collected', '4 Suspects Identified', '12 Communications Linked', '₹850,000 Suspicious Txns', 'Gang Network Connected'].map((item, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-xl font-semibold border-b border-border pb-2 text-primary">Recommended Police Actions</h3>
              <ul className="space-y-2 list-disc list-inside text-sm text-foreground">
                <li>Immediate deployment of additional patrols in Bengaluru South hotspot radius.</li>
                <li>Initiate surveillance on primary communication nodes identified in CDR analysis.</li>
                <li>Submit urgent request to freeze identified mule financial accounts.</li>
                <li>Issue BOLO (Be On Look Out) for primary suspects based on AI facial entity matching.</li>
              </ul>
            </div>
            
            <div className="text-center mt-8">
              <button 
                onClick={() => setStage('showcase')}
                className="text-sm text-muted-foreground hover:text-primary transition-colors underline"
              >
                Proceed to System Overview &rarr;
              </button>
            </div>
          </div>
        </div>
      )}

      {stage === 'showcase' && (
        <div className="w-full max-w-5xl text-center space-y-12 animate-in zoom-in-95 duration-1000 py-12">
          
          <div className="flex flex-col items-center justify-center space-y-4">
            <ShieldAlert className="h-24 w-24 text-primary animate-pulse" />
            <h1 className="text-5xl md:text-7xl font-bold font-heading tracking-tight text-foreground">
              Prahari AI
            </h1>
            <p className="text-xl md:text-3xl text-muted-foreground font-light">
              AI Powered Crime Intelligence Platform
            </p>
            <div className="mt-8 px-6 py-2 bg-secondary rounded-full border border-border">
              <p className="text-sm text-foreground font-medium uppercase tracking-widest">Built for Karnataka State Police</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-6 max-w-4xl mx-auto pt-8 border-t border-border">
            {['Zoho Catalyst', 'FastAPI', 'Next.js', 'Neo4j', 'PostgreSQL', 'Qdrant', 'Apache ECharts', 'Cytoscape', 'MapLibre', 'Gemini AI'].map((tech, i) => (
              <div key={i} className="p-3 bg-card border border-border rounded-lg shadow-sm text-sm font-medium text-muted-foreground">
                {tech}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto pt-8">
            <div className="flex flex-col items-center space-y-2">
              <Database className="h-8 w-8 text-blue-500" />
              <span className="text-3xl font-bold text-foreground">100k+</span>
              <span className="text-xs uppercase tracking-wider text-muted-foreground">Crime Records</span>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <Network className="h-8 w-8 text-indigo-500" />
              <span className="text-3xl font-bold text-foreground">30+</span>
              <span className="text-xs uppercase tracking-wider text-muted-foreground">Database Tables</span>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <Activity className="h-8 w-8 text-emerald-500" />
              <span className="text-3xl font-bold text-foreground">20+</span>
              <span className="text-xs uppercase tracking-wider text-muted-foreground">AI Modules</span>
            </div>
            <div className="flex flex-col items-center space-y-2">
              <ShieldAlert className="h-8 w-8 text-amber-500" />
              <span className="text-3xl font-bold text-foreground">15+</span>
              <span className="text-xs uppercase tracking-wider text-muted-foreground">Dashboards</span>
            </div>
          </div>
          
          <div className="pt-12">
            <h2 className="text-2xl font-bold font-heading text-primary">Thank You</h2>
          </div>
        </div>
      )}

    </div>
  )
}
