"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useUIStore } from "@/lib/stores/ui.store"
import {
  LayoutDashboard,
  FileText,
  Users,
  Search,
  Map as MapIcon,
  Activity,
  Network,
  Shield,
  Briefcase,
  Layers,
  Settings,
  BrainCircuit,
  PieChart
} from "lucide-react"

export function Sidebar() {
  const { sidebarOpen, activePortal, setActivePortal } = useUIStore()
  const pathname = usePathname()

  const adminLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "FIR Registry", href: "/cases", icon: FileText },
    { name: "Persons of Interest", href: "/persons", icon: Users },
    { name: "Global Search", href: "/search", icon: Search },
    { name: "Evidence & Media", href: "/media", icon: Layers },
    { name: "Audit Trail", href: "/audit", icon: Shield },
  ]

  const intelLinks = [
    { name: "Command Center", href: "/overview", icon: Activity },
    { name: "Geospatial Intelligence", href: "/map", icon: MapIcon },
    { name: "Network Link Analysis", href: "/network", icon: Network },
    { name: "Predictive Insights", href: "/predictions", icon: BrainCircuit },
    { name: "Analytical Trends", href: "/trends", icon: PieChart },
  ]

  const links = activePortal === "admin" ? adminLinks : intelLinks

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-card text-card-foreground transition-all duration-300 ease-in-out md:static",
        sidebarOpen ? "w-64 translate-x-0" : "w-20 -translate-x-full md:translate-x-0"
      )}
    >
      <div className="flex h-16 items-center justify-center border-b border-border px-4">
        <div className="flex items-center gap-2 font-heading font-bold text-xl text-primary dark:text-accent">
          <Shield className="h-6 w-6" />
          <span className={cn(sidebarOpen ? "block" : "hidden md:hidden")}>Prahari AI</span>
        </div>
      </div>

      <div className="flex-1 overflow-auto py-4">
        <nav className="space-y-1 px-2">
          {links.map((link) => {
            const Icon = link.icon
            const isActive = pathname.startsWith(link.href)
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary dark:bg-accent/20 dark:text-accent"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
                title={!sidebarOpen ? link.name : undefined}
              >
                <Icon className={cn("h-5 w-5 flex-shrink-0", isActive && "text-accent")} />
                <span className={cn("truncate", !sidebarOpen && "hidden md:hidden")}>
                  {link.name}
                </span>
              </Link>
            )
          })}
        </nav>
      </div>

      <div className="border-t border-border p-4">
        <div className="flex flex-col gap-2">
          <button
            onClick={() => setActivePortal(activePortal === "admin" ? "intelligence" : "admin")}
            className="flex items-center justify-center gap-2 rounded-md bg-secondary px-3 py-2 text-sm font-medium text-foreground hover:bg-secondary/80 transition-colors"
          >
            <Briefcase className="h-4 w-4 text-accent" />
            <span className={cn(!sidebarOpen && "hidden md:hidden")}>
              Switch to {activePortal === "admin" ? "Intel" : "Admin"}
            </span>
          </button>
          
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-foreground",
              !sidebarOpen && "justify-center"
            )}
          >
            <Settings className="h-5 w-5 flex-shrink-0" />
            <span className={cn(!sidebarOpen && "hidden md:hidden")}>Settings</span>
          </Link>
        </div>
      </div>
    </aside>
  )
}
