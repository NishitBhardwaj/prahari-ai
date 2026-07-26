"use client"

import { use } from "react"

import { useState } from "react"
import { ShieldAlert, Network, Merge, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function ResolutionCenterPage({ params }: { params: Promise<{ id: string }> }) {
  // Mocking the data for the UI
  const [resolutions, setResolutions] = useState([
    {
      id: "RES_1",
      source_entity: { type: "PERSON", name: "Ravi Kumar", id: "PER_NEW123" },
      target_entity: { type: "PERSON", name: "Ravi K.", id: "PER_MASTER890" },
      confidence: 89,
      reasons: ["Phone number match (9876543210)", "Name phonetic similarity"],
      status: "PENDING"
    },
    {
      id: "RES_2",
      source_entity: { type: "VEHICLE", name: "KA-01-AB-1234", id: "VEH_NEW456" },
      target_entity: { type: "VEHICLE", name: "KA01AB1234", id: "VEH_MASTER456" },
      confidence: 98,
      reasons: ["Exact License Plate Match (Normalized)"],
      status: "PENDING"
    }
  ])

  const handleMerge = (id: string) => {
    setResolutions(prev => prev.map(r => r.id === id ? { ...r, status: "MERGED" } : r))
  }

  const handleReject = (id: string) => {
    setResolutions(prev => prev.map(r => r.id === id ? { ...r, status: "REJECTED" } : r))
  }

  const pendingCount = resolutions.filter(r => r.status === "PENDING").length

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="p-6 border-b border-border flex items-center justify-between bg-card">
        <div>
          <h2 className="text-2xl font-heading font-semibold">Entity Resolution Center</h2>
          <p className="text-muted-foreground text-sm mt-1">Review AI-detected duplicate entities to maintain graph integrity.</p>
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1.5 bg-warning/10 text-warning rounded-full text-sm font-semibold border border-warning/20">
          <ShieldAlert className="h-4 w-4" />
          {pendingCount} Pending Reviews
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        {resolutions.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">No pending resolutions.</div>
        ) : (
          <div className="max-w-4xl space-y-6">
            {resolutions.map(res => (
              <div key={res.id} className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Network className="h-5 w-5 text-primary" />
                    <h3 className="font-semibold">Potential Duplicate Detected</h3>
                  </div>
                  {res.status === "PENDING" && (
                    <div className="text-sm font-mono bg-primary/10 text-primary px-2 py-1 rounded border border-primary/20">
                      {res.confidence}% Match
                    </div>
                  )}
                  {res.status === "MERGED" && <div className="text-sm text-success flex items-center gap-1"><CheckCircle2 className="h-4 w-4" /> Merged</div>}
                  {res.status === "REJECTED" && <div className="text-sm text-muted-foreground flex items-center gap-1">Kept Separate</div>}
                </div>
                
                <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-6 mb-6">
                  {/* Source (New) */}
                  <div className="bg-muted/30 p-4 rounded-lg border border-border">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider mb-1 block">New Entry (Case Draft)</span>
                    <p className="font-semibold text-lg">{res.source_entity.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{res.source_entity.id}</p>
                  </div>
                  
                  {/* Direction */}
                  <div className="flex flex-col items-center text-muted-foreground">
                    <ArrowRight className="h-6 w-6" />
                    <span className="text-[10px] mt-1">MERGE INTO</span>
                  </div>
                  
                  {/* Target (Master) */}
                  <div className="bg-primary/5 p-4 rounded-lg border border-primary/20">
                    <span className="text-[10px] uppercase font-bold text-primary tracking-wider mb-1 block">Master Graph Node</span>
                    <p className="font-semibold text-lg">{res.target_entity.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{res.target_entity.id}</p>
                  </div>
                </div>
                
                <div className="bg-muted/50 rounded-lg p-3 text-sm mb-6">
                  <span className="font-semibold flex items-center gap-2 mb-2"><AlertTriangle className="h-4 w-4 text-warning" /> AI Reasoning:</span>
                  <ul className="list-disc list-inside text-muted-foreground space-y-1">
                    {res.reasons.map((reason, i) => (
                      <li key={i}>{reason}</li>
                    ))}
                  </ul>
                </div>
                
                {res.status === "PENDING" && (
                  <div className="flex justify-end gap-3 border-t border-border pt-4">
                    <Button variant="outline" onClick={() => handleReject(res.id)}>Keep Separate</Button>
                    <Button onClick={() => handleMerge(res.id)}><Merge className="h-4 w-4 mr-2" /> Soft Merge Records</Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}