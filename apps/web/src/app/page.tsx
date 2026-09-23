"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { SemanticGraphWorkspace } from "@/modules/graph/GraphWorkspace";
import { OrchestrationMonitor } from "@/modules/orchestration/OrchestrationMonitor";
import ResearchWorkspace from "@/modules/research/ResearchWorkspace";
import TimelineWorkspace from "@/modules/timeline/TimelineWorkspace";
import AgentsWorkspace from "@/modules/agents/AgentsWorkspace";
import MemoryWorkspace from "@/modules/memory/MemoryWorkspace";
import ReflectionWorkspace from "@/modules/reflection/ReflectionWorkspace";
import StrategicWorkspace from "@/modules/strategic/StrategicWorkspace";
import SettingsWorkspace from "@/modules/settings/SettingsWorkspace";
import { useWorkspaceStore } from "@/stores/workspace";

export default function Home() {
  const { activeModule } = useWorkspaceStore();

  const renderModule = () => {
    switch (activeModule) {
      case "graph":
        return <SemanticGraphWorkspace />;
      case "orchestration":
        return <OrchestrationMonitor />;
      case "research":
        return <ResearchWorkspace />;
      case "timeline":
        return <TimelineWorkspace />;
      case "agents":
        return <AgentsWorkspace />;
      case "memory":
        return <MemoryWorkspace />;
      case "reflection":
        return <ReflectionWorkspace />;
      case "strategic":
        return <StrategicWorkspace />;
      case "settings":
        return <SettingsWorkspace />;
      default:
        return (
          <div className="h-full flex items-center justify-center flex-col space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-primary/10 flex items-center justify-center text-primary">
              <span className="font-bold text-2xl">C</span>
            </div>
            <div className="text-center">
              <h2 className="text-xl font-bold tracking-tight uppercase">Module In Deep Development</h2>
              <p className="text-sm text-slate-500">The cognitive layer for {activeModule} is being orchestrated.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <DashboardLayout>
      {renderModule()}
    </DashboardLayout>
  );
}
