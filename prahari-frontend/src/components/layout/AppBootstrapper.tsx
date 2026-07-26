"use client"

import { useState, useEffect } from "react"
import { BootScreen } from "./BootScreen"

export function AppBootstrapper({ children }: { children: React.ReactNode }) {
  const [booting, setBooting] = useState(true)

  // Avoid showing boot screen on hard refreshes during dev if desired, 
  // but for hackathon demo we always show it on first load.
  useEffect(() => {
    const hasBooted = sessionStorage.getItem("prahari_booted")
    if (hasBooted) {
      setBooting(false)
    }
  }, [])

  const handleBootComplete = () => {
    sessionStorage.setItem("prahari_booted", "true")
    setBooting(false)
  }

  if (booting) {
    return <BootScreen onComplete={handleBootComplete} />
  }

  return <>{children}</>
}
