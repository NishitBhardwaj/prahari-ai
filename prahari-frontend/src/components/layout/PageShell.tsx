"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { Header } from "./Header"
import { Sidebar } from "./Sidebar"
import { cn } from "@/lib/utils"
import { X, Sparkles, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { LiveDemoButton } from "../demo/LiveDemoButton"
import { DemoConclusion } from "../demo/DemoConclusion"
import { SystemHealth } from "../analytics/SystemHealth"
import { useGuidedScenario } from "@/hooks/useGuidedScenario"

export function PageShell({ children }: { children: React.ReactNode }) {
  const { assistantOpen, toggleAssistant, presentationMode, demoActive, showDemoConclusion } = useUIStore()
  
  // Mount the global scenario driver
  useGuidedScenario()

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {!presentationMode && <Sidebar />}
      <div className="flex flex-1 flex-col overflow-hidden">
        {!presentationMode && <Header />}
        
        {/* Main Content Area */}
        <div className="relative flex flex-1 overflow-hidden">
          <main className={cn(
            "flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 transition-all duration-300",
            assistantOpen && !presentationMode ? "mr-80" : "mr-0"
          )}>
            {children}
          </main>
          
          {/* Persistent AI Assistant Drawer */}
          <aside
            className={cn(
              "absolute right-0 top-0 z-30 flex h-full w-80 flex-col border-l border-border bg-card shadow-xl transition-transform duration-300 ease-in-out",
              assistantOpen ? "translate-x-0" : "translate-x-full"
            )}
          >
            <div className="flex items-center justify-between border-b border-border p-4">
              <div className="flex items-center gap-2 text-accent font-heading font-semibold">
                <Sparkles className="h-5 w-5" />
                <span>Prahari AI Assistant</span>
              </div>
              <Button variant="ghost" size="icon" onClick={toggleAssistant}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {demoActive ? (
                <div className="rounded-lg bg-amber-500/10 border border-amber-500/30 p-4 text-sm text-foreground space-y-3 animate-pulse">
                  <div className="font-semibold text-amber-500 flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                    </span>
                    Live Narration
                  </div>
                  <p>A Priority 1 Incident has just been reported in Bengaluru South.</p>
                  <p>I am automatically drafting FIR CASE-DEMO-001.</p>
                  <p>My Risk Engine identifies an 85% probability that this is linked to the 'Bawariya Gang' based on historical M.O. and geospatial clustering.</p>
                  <p>Navigating to Crime Map to visualize the geospatial threat radius...</p>
                </div>
              ) : (
                <div className="rounded-lg bg-secondary p-3 text-sm text-foreground">
                  Hello Officer. I can help you analyze case relationships, summarize evidence, or retrieve standard operating procedures. How can I assist you today?
                </div>
              )}
            </div>
            
            <div className="border-t border-border p-4">
              <div className="relative flex items-center">
                <input 
                  type="text" 
                  placeholder="Ask about cases, evidence..." 
                  className="w-full rounded-full border border-input bg-background px-4 py-2 pr-10 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
                <Button size="icon" variant="ghost" className="absolute right-1 h-8 w-8 rounded-full text-primary dark:text-accent">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </aside>
        </div>
      </div>
      
      {/* Floating Action Button for AI Assistant (visible when closed) */}
      {!assistantOpen && (
        <Button
          onClick={toggleAssistant}
          size="icon"
          className="absolute bottom-6 right-6 h-14 w-14 rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 dark:bg-accent dark:text-primary dark:hover:bg-accent/90 z-40 transition-transform hover:scale-105"
        >
          <Sparkles className="h-6 w-6" />
        </Button>
      )}

      <LiveDemoButton />
      <SystemHealth />
      {showDemoConclusion && <DemoConclusion />}
    </div>
  )
}
