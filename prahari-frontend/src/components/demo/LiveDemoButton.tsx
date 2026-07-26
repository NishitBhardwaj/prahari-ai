"use client"

import { Button } from "@/components/ui/button"
import { Clapperboard, Play, Square, RotateCcw } from "lucide-react"
import { useUIStore } from "@/lib/stores/ui.store"
import { cn } from "@/lib/utils"
import { useState, useEffect } from "react"

export function LiveDemoButton() {
  const { demoActive, setDemoActive, togglePresentationMode, presentationMode } = useUIStore()
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!demoActive) {
      setProgress(0)
      return
    }
    // Demo is ~29 seconds total (4s + 5s + 7s + 8s + 5s)
    const totalMs = 29000
    const interval = 100
    const step = (interval / totalMs) * 100
    
    const timer = setInterval(() => {
      setProgress(p => Math.min(100, p + step))
    }, interval)
    
    return () => clearInterval(timer)
  }, [demoActive])

  const handleStartDemo = () => {
    if (!presentationMode) togglePresentationMode()
    setDemoActive(true)
    
    // The useGuidedScenario hook will listen to demoActive and drive the navigation.
  }

  const handleStopDemo = () => {
    setDemoActive(false)
    if (presentationMode) togglePresentationMode()
  }

  const handleResetDemo = () => {
    // Quick reset for hackathon pacing
    setDemoActive(false)
    setTimeout(() => {
      setDemoActive(true)
    }, 100)
  }

  return (
    <div className="fixed bottom-6 left-6 z-50 flex items-center gap-2">
      {!demoActive ? (
        <Button 
          onClick={handleStartDemo}
          className="rounded-full bg-amber-500 hover:bg-amber-600 text-white shadow-xl shadow-amber-500/20 font-bold px-6 py-6 border-2 border-amber-300 animate-pulse"
        >
          <Clapperboard className="mr-2 h-5 w-5" />
          🎬 Start Demo Scenario
        </Button>
      ) : (
        <div className="flex items-center gap-2 bg-card p-2 rounded-full border border-border shadow-2xl relative overflow-hidden">
          <div 
            className="absolute left-0 bottom-0 h-1 bg-amber-500/50 transition-all duration-100" 
            style={{ width: `${progress}%` }} 
          />
          <div className="relative z-10 flex items-center gap-2 px-4 text-amber-500 font-bold animate-pulse">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
            </span>
            Guided Demo Running...
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            className="rounded-full px-4 font-bold shadow-lg bg-background"
            onClick={handleResetDemo}
          >
            <RotateCcw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          <Button 
            variant="destructive" 
            size="sm" 
            className="rounded-full px-6 font-bold shadow-lg"
            onClick={handleStopDemo}
          >
            <Square className="mr-2 h-4 w-4" />
            Take Control
          </Button>
        </div>
      )}
    </div>
  )
}
