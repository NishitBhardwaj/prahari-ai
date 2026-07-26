"use client"

import { use } from "react"

import { useState } from "react"
import { useCaseEvidence } from "@/lib/api/queries"
import { Loader2, FileBox, FileImage, FileText, Smartphone, HardDrive, FileAudio, FileVideo, Shield, UploadCloud, Search, List, LayoutGrid, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

function getEvidenceIcon(type: string) {
  const t = type.toUpperCase()
  if (t.includes("PHONE") || t.includes("MOBILE")) return <Smartphone className="h-10 w-10 text-primary" />
  if (t.includes("DRIVE") || t.includes("LAPTOP")) return <HardDrive className="h-10 w-10 text-primary" />
  if (t.includes("PHOTO") || t.includes("IMAGE")) return <FileImage className="h-10 w-10 text-primary" />
  if (t.includes("AUDIO") || t.includes("CALL")) return <FileAudio className="h-10 w-10 text-primary" />
  if (t.includes("CCTV") || t.includes("VIDEO")) return <FileVideo className="h-10 w-10 text-primary" />
  if (t.includes("DOCUMENT") || t.includes("REPORT")) return <FileText className="h-10 w-10 text-primary" />
  return <FileBox className="h-10 w-10 text-primary" />
}

export default function EvidencePage({ params }: { params: Promise<{ id: string }> }) {
  const { data, isLoading } = useCaseEvidence(use(params).id)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  
  if (isLoading) {
    return <div className="h-full flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
  }

  const evidenceList = data?.data || []

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="p-6 border-b border-border flex items-center justify-between bg-card">
        <div>
          <h2 className="text-2xl font-heading font-semibold">Evidence & Chain of Custody</h2>
          <p className="text-muted-foreground text-sm mt-1">Manage physical and digital assets linked to this case.</p>
        </div>
        
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input className="pl-9 w-64" placeholder="Search evidence..." />
          </div>
          <div className="flex border rounded-md">
            <Button variant={viewMode === "grid" ? "secondary" : "ghost"} size="icon" onClick={() => setViewMode("grid")} className="rounded-r-none border-r"><LayoutGrid className="h-4 w-4" /></Button>
            <Button variant={viewMode === "list" ? "secondary" : "ghost"} size="icon" onClick={() => setViewMode("list")} className="rounded-l-none"><List className="h-4 w-4" /></Button>
          </div>
          <Button>
            <UploadCloud className="mr-2 h-4 w-4" />
            Log Evidence
          </Button>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        {evidenceList.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground border-2 border-dashed border-border rounded-xl">
            <FileBox className="h-12 w-12 mb-4 opacity-20" />
            <p>No evidence logged for this case.</p>
          </div>
        ) : (
          <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "space-y-4"}>
            {evidenceList.map((ev: any) => (
              <div 
                key={ev.evidence_id} 
                className={`bg-card border border-border rounded-xl overflow-hidden hover:shadow-md transition-all group ${viewMode === "list" ? "flex items-center gap-6 p-4" : ""}`}
              >
                {/* Visual Preview Area */}
                <div className={`${viewMode === "grid" ? "h-40 bg-muted/30 border-b border-border flex items-center justify-center relative overflow-hidden" : "h-16 w-16 bg-muted rounded-md flex items-center justify-center flex-shrink-0"}`}>
                  {getEvidenceIcon(ev.evidence_type || "")}
                  {viewMode === "grid" && (
                    <div className="absolute inset-0 bg-background/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <Button variant="secondary">View Details</Button>
                    </div>
                  )}
                </div>
                
                {/* Meta Details */}
                <div className={`${viewMode === "grid" ? "p-5" : "flex-1 flex justify-between items-center"}`}>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-sm">
                        {ev.evidence_number}
                      </span>
                      {ev.versions?.length > 0 && (
                        <span className="flex items-center gap-1 text-[10px] text-muted-foreground bg-muted px-2 py-0.5 rounded-full" title="Digital files attached">
                          <HardDrive className="h-3 w-3" /> v{ev.versions.length}
                        </span>
                      )}
                    </div>
                    <h4 className="font-semibold">{ev.evidence_type?.replace("_", " ")}</h4>
                    {viewMode === "grid" && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mt-2">{ev.description || "No description provided."}</p>
                    )}
                  </div>
                  
                  <div className={`${viewMode === "grid" ? "mt-4 pt-4 border-t border-border flex items-center justify-between" : "flex items-center gap-6 text-right"}`}>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Shield className="h-3 w-3 text-success" />
                      <span>Custody Intact</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{ev.seizure_date ? new Date(ev.seizure_date).toLocaleDateString() : "Pending"}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}