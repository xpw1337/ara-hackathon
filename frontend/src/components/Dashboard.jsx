import { useState, useEffect } from "react";
import WorkflowCard from "./WorkflowCard";
import { api, WORKFLOW_IDS } from "../api/client";
import { Zap, TrendingUp, Calendar, BookOpen, RefreshCw, AlertCircle } from "lucide-react";

const WORKFLOWS = [
  {
    id: WORKFLOW_IDS.RESEARCH_LOG,
    title: "Research Log Sync",
    description: "Pull WakaTime activity → write weekly log",
  },
  {
    id: WORKFLOW_IDS.ADVISOR_UPDATE,
    title: "Advisor Update Draft",
    description: "Summarize GitHub commits → Gmail draft",
  },
  {
    id: WORKFLOW_IDS.PAPER_SCOUT,
    title: "Paper Scout",
    description: "Search arXiv → update reading list",
  },
  {
    id: WORKFLOW_IDS.DEADLINE_GUARDIAN,
    title: "Deadline Guardian",
    description: "Canvas + Calendar → 48hr reminders",
  },
  {
    id: WORKFLOW_IDS.WEEK_PLANNER,
    title: "Sunday Week Planner",
    description: "Todoist + deadlines → prioritized plan",
  },
];

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [runningWorkflows, setRunningWorkflows] = useState({});

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
      setError(err.message || "Failed to load dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunWorkflow = async (workflowId) => {
    // Set running state
    setRunningWorkflows((prev) => ({ ...prev, [workflowId]: true }));

    try {
      const result = await api.runWorkflow(workflowId);

      // Update workflow state in dashboard data
      setDashboardData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          generatedAt: new Date().toISOString(),
          workflows: {
            ...prev.workflows,
            [workflowId]: {
              status: result.ok ? "success" : "error",
              lastRun: result.generated_at,
              summary: result.summary,
              artifacts: result.artifacts,
              errors: result.errors,
            },
          },
        };
      });
    } catch (err) {
      // Update with error state
      setDashboardData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          workflows: {
            ...prev.workflows,
            [workflowId]: {
              ...prev.workflows[workflowId],
              status: "error",
              errors: [err.message || "Workflow failed"],
            },
          },
        };
      });
    } finally {
      setRunningWorkflows((prev) => ({ ...prev, [workflowId]: false }));
    }
  };

  // Loading state
  if (isLoading && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="card-brutal bg-brutal-yellow p-8 text-center">
          <RefreshCw className="w-12 h-12 mx-auto mb-4 animate-spin" />
          <p className="font-bold text-xl">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Error state (with no data)
  if (error && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="card-brutal bg-brutal-coral p-8 text-center max-w-md">
          <AlertCircle className="w-12 h-12 mx-auto mb-4" />
          <p className="font-bold text-xl mb-2">Failed to load dashboard</p>
          <p className="font-mono text-sm mb-4">{error}</p>
          <button onClick={loadDashboardData} className="btn-brutal">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const { stats, workflows, generatedAt, recentArtifacts } = dashboardData || {};

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="card-brutal bg-brutal-yellow">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold mb-2">Hey, Researcher! 👋</h1>
            <p className="font-mono text-lg">
              Your academic ops dashboard. Let's keep you on track.
            </p>
            {generatedAt && (
              <p className="font-mono text-sm opacity-70 mt-2">
                Last updated: {new Date(generatedAt).toLocaleString()}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <div className="w-16 h-16 bg-brutal-pink border-3 border-brutal-black shape-blob"></div>
            <div className="w-16 h-16 bg-brutal-lime border-3 border-brutal-black shape-star"></div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Zap className="w-8 h-8" />}
          value={`${stats?.codingHours ?? 0}h`}
          label="Coding This Week"
          color="bg-brutal-mint"
        />
        <StatCard
          icon={<TrendingUp className="w-8 h-8" />}
          value={stats?.commits ?? 0}
          label="Commits"
          color="bg-brutal-purple"
        />
        <StatCard
          icon={<Calendar className="w-8 h-8" />}
          value={stats?.upcomingDeadlines ?? 0}
          label="Deadlines Soon"
          color="bg-brutal-coral"
        />
        <StatCard
          icon={<BookOpen className="w-8 h-8" />}
          value={stats?.papersFound ?? 0}
          label="New Papers"
          color="bg-brutal-cyan"
        />
      </div>

      {/* Section Header */}
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold">Workflows</h2>
        <div className="flex-1 h-1 bg-brutal-black"></div>
        <button
          onClick={loadDashboardData}
          disabled={isLoading}
          className={`btn-brutal-outline text-sm py-2 flex items-center gap-2
            ${isLoading ? "opacity-50" : ""}`}
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Workflow Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {WORKFLOWS.map((workflow) => {
          const workflowState = workflows?.[workflow.id] || {};
          const isRunning = runningWorkflows[workflow.id];

          return (
            <WorkflowCard
              key={workflow.id}
              id={workflow.id}
              title={workflow.title}
              description={workflow.description}
              status={isRunning ? "running" : workflowState.status || "idle"}
              lastRun={workflowState.lastRun}
              summary={workflowState.summary}
              artifacts={workflowState.artifacts || []}
              errors={workflowState.errors || []}
              onRun={() => handleRunWorkflow(workflow.id)}
            />
          );
        })}
      </div>

      {/* Recent Artifacts */}
      {recentArtifacts && recentArtifacts.length > 0 && (
        <>
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold">Recent Artifacts</h2>
            <div className="flex-1 h-1 bg-brutal-black"></div>
          </div>
          <div className="card-brutal bg-brutal-white">
            <div className="space-y-3">
              {recentArtifacts.map((artifact, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 border-2 border-brutal-black bg-brutal-cream"
                >
                  <span className="text-xl">
                    {artifact.type === "gmail_draft" ? "✉️" : "📄"}
                  </span>
                  <div className="flex-1">
                    <p className="font-bold">{artifact.title}</p>
                    <p className="text-sm font-mono opacity-70">
                      from {artifact.workflow}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ icon, value, label, color }) {
  return (
    <div className={`card-brutal ${color} text-center`}>
      <div className="flex justify-center mb-2">{icon}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="font-mono text-sm">{label}</div>
    </div>
  );
}