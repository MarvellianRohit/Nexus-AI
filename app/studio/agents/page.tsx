import { AgentManager } from '@/components/agents/AgentManager';

export default function AgentsPage() {
    return (
        <div className="h-full w-full overflow-y-auto bg-background p-4">
            <AgentManager />
        </div>
    );
}
