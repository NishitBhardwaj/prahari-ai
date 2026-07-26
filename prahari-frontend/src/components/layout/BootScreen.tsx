"use client"

import { useEffect, useState } from "react"
import { ShieldAlert, Check } from "lucide-react"

export function BootScreen({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0)

  const steps = [
    "Connecting to PostgreSQL...",
    "Connecting to Neo4j...",
    "Loading Knowledge Graph...",
    "Loading AI Models...",
    "Connecting to Zoho Catalyst...",
    "Initializing Intelligence Engine...",
    "Loading Karnataka Crime Map...",
    "System Ready"
  ]

  useEffect(() => {
    let currentStep = 0
    const interval = setInterval(() => {
      currentStep++
      if (currentStep <= steps.length) {
        setStep(currentStep)
      } else {
        clearInterval(interval)
        setTimeout(() => onComplete(), 500)
      }
    }, 600) // ~5 seconds total

    return () => clearInterval(interval)
  }, [onComplete, steps.length])

  return (
    <div className="fixed inset-0 z-[100] bg-zinc-950 flex flex-col items-center justify-center text-zinc-100 overflow-hidden font-mono">
      {/* Particle background effect (simplified css animation) */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-500 rounded-full blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-40 h-40 bg-indigo-500 rounded-full blur-[120px] animate-pulse delay-700"></div>
      </div>

      <div className="relative z-10 w-full max-w-md p-8">
        <div className="flex flex-col items-center mb-12">
          <ShieldAlert className="h-16 w-16 text-blue-500 mb-4 animate-bounce" />
          <h1 className="text-4xl font-bold tracking-widest text-center">PRAHARI AI</h1>
          <p className="text-zinc-400 mt-2 text-center text-sm tracking-wide">Karnataka State Police Crime Intelligence Platform</p>
          <div className="mt-4 px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-bold border border-blue-500/30">
            Prototype v1.0
          </div>
        </div>

        <div className="space-y-3">
          {steps.map((text, i) => (
            <div 
              key={i} 
              className={`flex items-center gap-3 text-sm transition-all duration-300 ${
                i < step ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
              }`}
            >
              {i < step && i !== steps.length - 1 && (
                <Check className="h-4 w-4 text-emerald-500" />
              )}
              {i === steps.length - 1 && i < step && (
                <ShieldAlert className="h-4 w-4 text-blue-500" />
              )}
              <span className={i === steps.length - 1 ? "text-blue-400 font-bold" : "text-zinc-300"}>
                {text}
              </span>
            </div>
          ))}
        </div>

        {/* Loading Bar */}
        <div className="mt-12 h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 transition-all duration-500 ease-out"
            style={{ width: `${Math.min(100, (step / steps.length) * 100)}%` }}
          />
        </div>
      </div>
    </div>
  )
}
