import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Flame, ShieldAlert, Users } from "lucide-react"

export function KPIBar() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card className="bg-card border-border shadow-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Cases (YTD)</CardTitle>
          <ShieldAlert className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold font-heading">24,591</div>
          <p className="text-xs text-muted-foreground">
            +4% from last year
          </p>
        </CardContent>
      </Card>
      <Card className="bg-card border-border shadow-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Hotspots</CardTitle>
          <Flame className="h-4 w-4 text-amber-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold font-heading text-amber-500">14</div>
          <p className="text-xs text-muted-foreground">
            3 High Risk Zones
          </p>
        </CardContent>
      </Card>
      <Card className="bg-card border-border shadow-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tracked Gangs</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold font-heading">47</div>
          <p className="text-xs text-muted-foreground">
            12 currently active
          </p>
        </CardContent>
      </Card>
      <Card className="bg-card border-border shadow-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">AI Risk Alerts</CardTitle>
          <AlertCircle className="h-4 w-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold font-heading text-red-500">8</div>
          <p className="text-xs text-muted-foreground">
            Requires immediate review
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
