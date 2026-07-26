export default function OverviewPage() {
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex flex-row justify-between items-end">
        <div>
          <h2 className="text-3xl font-heading font-bold tracking-tight text-accent">Command Center</h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Live Intelligence Dashboard. Monitoring all active spatial and network threats.
          </p>
        </div>
        <div className="flex gap-2">
          {/* Action buttons placeholder */}
          <button className="px-4 py-2 bg-secondary text-sm font-medium rounded-md hover:bg-secondary/80">Export Report</button>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="rounded-xl border border-border bg-card text-card-foreground p-6 shadow-sm">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Predicted Hotspots</h3>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" className="h-4 w-4 text-destructive"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
            </div>
            <div className="text-2xl font-bold font-mono text-destructive">12 High Risk</div>
            <p className="text-xs text-muted-foreground mt-1">Requiring immediate patrol dispatch</p>
          </div>
        ))}
      </div>

      <div className="flex-1 min-h-[400px] rounded-xl border border-border bg-card p-0 flex relative overflow-hidden">
        {/* Map Placeholder */}
        <div className="absolute inset-0 bg-secondary flex items-center justify-center text-muted-foreground">
          MapLibre GL JS Container Placeholder
        </div>
      </div>
    </div>
  )
}
