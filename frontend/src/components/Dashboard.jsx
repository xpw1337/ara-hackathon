import { useState, useEffect } from 'react'
import WorkflowCard from './WorkflowCard'
import { api } from '../api/client'
import { Zap, TrendingUp, Calendar, BookOpen, RefreshCw } from 'lucide-react'

const WORKFLOWS = [
  {
    id: 'research-log',
    title: 'Research Log Sync',
    description: 'Pull WakaTime activity → write weekly log',
  },
  {
    id: 'advisor-update',
    title: 'Advisor Update Draft',
    description: 'Summarize GitHub commits → Gmail draft',
  },
  {
    id: 'paper-scout',
    title: 'Paper Scout',
    description: 'Search arXiv → update reading list',
  },
  {
    id: 'deadline-guardian',
    title: 'Deadline Guardian',
    description: 'Canvas + Calendar → 48hr reminders',
  },
  {
    id: 'week-planner',
    title: 'Sunday Week Planner',
    description: 'Todoist + deadlines → prioritized plan',
  },
]

export default function Dashboard() {
  const [workflowStates, setWorkflowStates] = useState({})
  const [stats, setStats] = useState({
    codingHours: 0,
    commits: 0,
    upcomingDeadlines: 0,
    papersFound: 0,
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setIsLoading(true)
    try {
      const data = await api.getDashboard()
      
      // Normalize workflow states from backend contract
      const normalizedWorkflows = {}
      for (const [id, workflow] of Object.entries(data.workflows || {})) {
        normalizedWorkflows[id] = {
          status: workflow.status || (workflow.ok ? 'success' : 'error'),
          lastRun: workflow.lastRun,
          summary: workflow.summary,
          artifacts: workflow.artifacts || [],
          errors: workflow.errors || [],
        }
      }
      
      setWorkflowStates(normalizedWorkflows)
      setStats(data.stats || stats)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRunWorkflow = async (workflowId) => {
    // Set running state
    setWorkflowStates(prev => ({
      ...prev,
      [workflowId]: { ...prev[workflowId], status: 'running' }
    }))

    try {
      const result = await api.runWorkflow(workflowId)
      
      // Update with result (already normalized by client)
      setWorkflowStates(prev => ({
        ...prev,
        [workflowId]: {
          status: result.status,
          lastRun: result.timestamp,
          summary: result.summary,
          artifacts: result.artifacts,
          errors: result.errors,
        }
      }))
    } catch (err) {
      setWorkflowStates(prev => ({
        ...prev,
        [workflowId]: { 
          ...prev[workflowId], 
          status: 'error',
          errors: [err.message || 'Workflow failed']
        }
      }))
    }
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="card-brutal bg-brutal-yellow">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Hey, Researcher! 👋
            </h1>
            <p className="font-mono text-lg">
              Your academic ops dashboard. Let's keep you on track.
            </p>
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
          value={`${stats.codingHours}h`}
          label="Coding This Week"
          color="bg-brutal-mint"
        />
        <StatCard 
          icon={<TrendingUp className="w-8 h-8" />}
          value={stats.commits}
          label="Commits"
          color="bg-brutal-purple"
        />
        <StatCard 
          icon={<Calendar className="w-8 h-8" />}
          value={stats.upcomingDeadlines}
          label="Deadlines Soon"
          color="bg-brutal-coral"
        />
        <StatCard 
          icon={<BookOpen className="w-8 h-8" />}
          value={stats.papersFound}
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
            ${isLoading ? 'opacity-50' : ''}`}
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Workflow Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {WORKFLOWS.map(workflow => (
          <WorkflowCard
            key={workflow.id}
            {...workflow}
            status={workflowStates[workflow.id]?.status || 'idle'}
            lastRun={workflowStates[workflow.id]?.lastRun}
            summary={workflowStates[workflow.id]?.summary}
            artifacts={workflowStates[workflow.id]?.artifacts || []}
            errors={workflowStates[workflow.id]?.errors || []}
            onRun={() => handleRunWorkflow(workflow.id)}
          />
        ))}
      </div>
    </div>
  )
}

function StatCard({ icon, value, label, color }) {
  return (
    <div className={`card-brutal ${color} text-center`}>
      <div className="flex justify-center mb-2">{icon}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="font-mono text-sm">{label}</div>
    </div>
  )
}