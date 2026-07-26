"use client"

import { useEffect, useRef } from "react"
import { useUIStore } from "@/lib/stores/ui.store"
import { useRouter, usePathname } from "next/navigation"

export function useGuidedScenario() {
  const { demoActive, setDemoActive, setAssistantOpen, setShowDemoConclusion } = useUIStore()
  const router = useRouter()
  const pathname = usePathname()
  const sequenceTimer = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!demoActive) {
      if (sequenceTimer.current) clearTimeout(sequenceTimer.current)
      setShowDemoConclusion(false)
      return
    }

    const runSequence = async () => {
      // Step 1: Wait on Executive Dashboard, then open Assistant
      console.log("[Demo] Step 1: Dashboard")
      if (pathname !== "/dashboard") router.push("/dashboard")
      await new Promise(r => setTimeout(r, 4000))
      
      // Step 2: Open Assistant
      if (!useUIStore.getState().assistantOpen) {
        setAssistantOpen(true)
      }
      await new Promise(r => setTimeout(r, 5000))

      // Step 3: Navigate to Map
      console.log("[Demo] Step 3: Map")
      router.push("/map")
      await new Promise(r => setTimeout(r, 7000))

      // Step 4: Navigate to Network Intelligence
      console.log("[Demo] Step 4: Network")
      router.push("/intelligence/network")
      await new Promise(r => setTimeout(r, 8000))

      // Step 5: Navigate to Investigation Workspace (Cases)
      console.log("[Demo] Step 5: Cases")
      router.push("/cases")
      await new Promise(r => setTimeout(r, 5000))

      // Complete
      console.log("[Demo] Sequence Complete - Firing Conclusion")
      setShowDemoConclusion(true)
      // We keep demoActive true so the UI doesn't suddenly revert underneath the modal
      setAssistantOpen(false)
    }

    runSequence()

    return () => {
      if (sequenceTimer.current) clearTimeout(sequenceTimer.current)
    }
  }, [demoActive, router, pathname, setAssistantOpen, setDemoActive])
}
