"use client"

import { useUIStore } from "@/lib/stores/ui.store"
import { Search, Bell, Menu, User, ShieldAlert } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
  const { toggleSidebar, activePortal } = useUIStore()

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-border bg-background px-4 md:px-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle Sidebar</span>
        </Button>
        <div className="hidden md:flex flex-col">
          <h1 className="text-lg font-heading font-semibold text-foreground leading-tight">
            Prahari AI
          </h1>
          <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
            {activePortal === "admin" ? "Case Management Portal" : "Intelligence Command Center"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-4 flex-1 justify-end">
        {/* Global Search Bar (Placeholder) */}
        <div className="hidden lg:flex relative w-full max-w-md items-center">
          <Search className="absolute left-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search FIRs, Entities, Vehicles, Phones... (Cmd+K)"
            className="w-full rounded-md border border-input bg-secondary px-9 py-2 text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
          <div className="absolute right-2.5 flex items-center gap-1">
            <kbd className="inline-flex h-5 items-center gap-1 rounded border border-border bg-background px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">⌘</span>K
            </kbd>
          </div>
        </div>

        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
          <span className="sr-only">Notifications</span>
        </Button>
        
        <Button variant="ghost" size="icon" className="relative">
          <ShieldAlert className="h-5 w-5 text-accent" />
          <span className="sr-only">System Alerts</span>
        </Button>

        <Button variant="secondary" size="icon" className="rounded-full">
          <User className="h-5 w-5" />
          <span className="sr-only">User Profile</span>
        </Button>
      </div>
    </header>
  )
}
