"use client"

import { use } from "react"

import { useCaseTimeline } from "@/lib/api/queries"
import { Loader2, Activity, UserPlus, CheckCircle, AlertTriangle, FileText, Bot } from "lucide-react"
import { cn } from "@/lib/utils"

function getEventIcon(type: string) {
  switch(type) {
    case "FIR_DRAFT_CREATED": return <FileText className="h-4 w-4" />
    case "VICTIM_ADDED":
    case "ACCUSED_ADDED": return <UserPlus className="h-4 w-4" />
    case "TASK_CREATED": return <CheckCircle className="h-4 w-4" />
    case "AI_SCORE_UPDATED": return <Bot className="h-4 w-4" />
    default: return <Activity className="h-4 w-4" />
  }
}

function getEventColor(type: string) {
  switch(type) {
    case "FIR_DRAFT_CREATED": return "bg-blue-500/10 text-blue-500 border-blue-500/20"
    case "VICTIM_ADDED": return "bg-amber-500/10 text-amber-500 border-amber-500/20"
    case "ACCUSED_ADDED": return "bg-destructive/10 text-destructive border-destructive/20"
    case "TASK_CREATED": return "bg-success/10 text-success border-success/20"
    case "AI_SCORE_UPDATED": return "bg-purple-500/10 text-purple-500 border-purple-500/20"
    default: return "bg-muted text-muted-foreground border-border"
  }
}

export default function TimelinePage({ params }: { params: Promise<{ id: string }> }) {
  const { data, isLoading } = useCaseTimeline(use(params).id)

  if (isLoading) {
    return <div className="h-full flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
  }

  const events = data?.data || []

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-heading font-semibold">Universal Timeline</h2>
          <p className="text-muted-foreground text-sm mt-1">Single source of truth for all investigation events.</p>
        </div>
        
        {/* Filter Chips Placeholder */}
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-semibold cursor-pointer">All Events</span>
          <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-semibold cursor-pointer">Entity Updates</span>
          <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-semibold cursor-pointer">AI Insights</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">No events recorded yet.</div>
        ) : (
          <div className="relative border-l border-border ml-4 space-y-8">
            {events.map((event: any, idx: number) => {
              const dateObj = new Date(event.timestamp)
              const timeString = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              const dateString = dateObj.toLocaleDateString()

              return (
                <div key={event.event_id} className="relative pl-8">
                  {/* Timeline Dot */}
                  <div className={cn(
                    "absolute -left-3.5 top-1 h-7 w-7 rounded-full border flex items-center justify-center bg-card",
                    getEventColor(event.event_type)
                  )}>
                    {getEventIcon(event.event_type)}
                  </div>
                  
                  {/* Event Content */}
                  <div className="bg-muted/30 border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-foreground">{event.title}</h4>
                      <span className="text-xs text-muted-foreground font-mono bg-background px-2 py-1 rounded-md border">
                        {dateString} {timeString}
                      </span>
                    </div>
                    {event.description && (
                      <p className="text-sm text-muted-foreground mb-3">{event.description}</p>
                    )}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center text-[10px] text-primary">
                          {event.actor_name?.charAt(0) || "S"}
                        </div>
                        {event.actor_name || "System"}
                      </div>
                      
                      {/* Action Button Placeholder based on type */}
                      {event.event_type === "VICTIM_ADDED" && (
                        <button className="text-xs text-primary hover:underline">View in Resolution Center &rarr;</button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}