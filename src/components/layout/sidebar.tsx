import { LayoutDashboard, MessageSquareMore, PanelsTopLeft, Settings2, Sparkles } from "lucide-react";
import { NavLink } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Command Center", icon: LayoutDashboard },
  { to: "/clients", label: "Client 360", icon: PanelsTopLeft },
  { to: "/monthly-touches", label: "Monthly Touches", icon: MessageSquareMore },
  { to: "/prompts", label: "Prompt Center", icon: Sparkles },
  { to: "/settings", label: "Settings", icon: Settings2 },
];

export function Sidebar() {
  return (
    <aside className="flex h-full w-full flex-col rounded-[32px] border border-white/10 bg-[#07111f]/90 p-6 shadow-glow">
      <div className="space-y-4">
        <Badge>MTOS OS</Badge>
        <div>
          <p className="font-display text-3xl tracking-tight text-white">Monthly Touch</p>
          <p className="mt-2 max-w-[16rem] text-sm text-muted-foreground">
            The account management operating system for recurring client intelligence.
          </p>
        </div>
      </div>

      <nav className="mt-10 flex flex-1 flex-col gap-2">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-muted-foreground transition-all hover:bg-white/5 hover:text-white",
                isActive && "bg-white/10 text-white",
              )
            }
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="rounded-[24px] border border-emerald-400/20 bg-emerald-400/10 p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-emerald-200">AI Router</p>
        <p className="mt-2 text-sm text-white">Claude for strategy. Gemini for classification. Every run traced.</p>
      </div>
    </aside>
  );
}
