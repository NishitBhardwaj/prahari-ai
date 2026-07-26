"use client"

import { use } from "react"

import { useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useWorkspaceStore } from "@/lib/store/workspace-store"
import { cn } from "@/lib/utils"
import { 
  Activity, 
  CheckSquare, 
  FileBox, 
  FileVideo, 
  Network, 
  MessageSquare, 
  Banknote, 
  Scale, 
  ChevronRight,
  Bot
} from "lucide-react"
import { Button } from "@/components/ui/button"

const MODULES = [
  { name: "Timeline", icon: Activity, href: "timeline" },
  { name: "Task Board", icon: CheckSquare, href: "tasks" },
  { name: "Evidence & Custody", icon: FileBox, href: "evidence" },
  { name: "Media Intelligence", icon: FileVideo, href: "media" },
  { name: "Entity Resolution", icon: Network, href: "resolution" },
  { name: "Communications", icon: MessageSquare, href: "communications" },
  { name: "Financial Analysis", icon: Banknote, href: "financial" },
  { name: "Legal & Court", icon: Scale, href: "court" },
]

export default function WorkspaceLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ id: string }>
}) {
  const pathname = usePathname()
  const { setCaseId, isAiSidebarOpen, toggleAiSidebar } = useWorkspaceStore()

  useEffect(() => {
    setCaseId(use(params).id)
    return () => setCaseId(null)
  }, [use(params).id, setCaseId])

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden bg-background">
      {/* 1. Left Navigation Pane (Thin) */}
      <nav className="w-64 border-r border-border bg-card flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-border">
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
            Investigation Workspace
          </div>
          <div className="font-heading font-bold truncate" title={use(params).id}>
            {use(params).id}
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
          {MODULES.map((mod) => {
            const href = `/cases/${use(params).id}/${mod.href}`
            const isActive = pathname.startsWith(href)
            
            return (
              <Link key={mod.name} href={href}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary dark:bg-accent/20 dark:text-accent"
                      : "text-foreground hover:bg-muted"
                  )}
                >
                  <mod.icon className="h-4 w-4" />
                  {mod.name}
                </div>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* 2. Center Pane (Wide) */}
      <main className="flex-1 flex flex-col min-w-0 bg-background overflow-hidden relative">
        {children}
        
        {/* Toggle AI Sidebar Button (if closed) */}
        {!isAiSidebarOpen && (
          <Button 
            variant="outline" 
            size="icon" 
            className="absolute top-4 right-4 z-10 shadow-md rounded-full bg-card"
            onClick={toggleAiSidebar}
            title="Open Prahari AI"
          >
            <Bot className="h-5 w-5 text-primary" />
          </Button>
        )}
      </main>

      {/* 3. Right Pane - Context-Aware AI Assistant */}
      {isAiSidebarOpen && (
        <aside className="w-80 border-l border-border bg-card flex flex-col flex-shrink-0 transition-all duration-300">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <span className="font-heading font-semibold">Prahari AI</span>
            </div>
            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={toggleAiSidebar}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          
          {/* AI Chat Interface */}
          <div className="flex-1 flex flex-col p-4">
            <div className="flex-1 border border-border rounded-md bg-muted/30 p-4 mb-4 overflow-y-auto text-sm text-muted-foreground flex flex-col gap-4">
              <div className="bg-primary/10 p-3 rounded-lg text-foreground border border-primary/20">
                <p className="text-xs font-semibold text-primary mb-1">System Connected</p>
                Hello IO. I have synchronized with the Universal Timeline and Knowledge Graph for Case <span className="font-mono">{use(params).id}</span>. How can I assist with this investigation?
              </div>
            </div>
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="Ask about this case..." 
                className="flex-1 bg-background border border-input rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <Button size="sm">Send</Button>
            </div>
          </div>
        </aside>
      )}
    </div>
  )
}