import { PageShell } from "@/components/layout/PageShell"
import { AppBootstrapper } from "@/components/layout/AppBootstrapper"

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AppBootstrapper>
      <PageShell>{children}</PageShell>
    </AppBootstrapper>
  )
}
