import { useState } from 'react'
import { Play, Clock, FileText, ExternalLink, AlertTriangle, Check } from 'lucide-react'
import StatusBadge from './StatusBadge'

const CARD_COLORS = {
  'research-log': 'bg-brutal-lime',
  'advisor-update': 'bg-brutal-pink',
  'paper-scout': 'bg-brutal-purple',
  'deadline-guardian': 'bg-brutal-coral',
  'week-planner': 'bg-brutal-cyan',
}

const CARD_ICONS = {
  'research-log': '📊',
  'advisor-update': '✉️',
  'paper-scout': '📚',
  'deadline-guardian': '⏰',
  'week-planner': '📋',
}

export default function WorkflowCard({ 
  id,
  title, 
  description, 
  status = 'idle',
  lastRun,
  summary,
  artifacts = [],
  errors = [],
  onRun 
}) {
  const [isExpanded, setIsExpanded] = useState(false)
  const bgColor = CARD_COLORS[id] || 'bg-brutal-white'
  const icon = CARD_ICONS[id] || '⚙️'

  const formatTimestamp = (ts) => {
    if (!ts) return null
    const date = new Date(ts)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true 
    })
  }

  return (
    <div className={`card-brutal ${bgColor} relative overflow-hidden`}>
      {/* Decorative corner */}
      <div className="absolute -top-2 -right-2 w-12 h-12 bg-brutal-black transform rotate-45"></div>
      
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-4xl">{icon}</span>
          <div>
            <h3 className="font-bold text-xl">{title}</h3>
            <p className="text-sm font-mono opacity-70">{description}</p>
          </div>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* Last Run Info */}
      {lastRun && (
        <div className="flex items-center gap-2 mb-4 text-sm font-mono">
          <Clock className="w-4 h-4" />
          <span>Last run: {formatTimestamp(lastRun)}</span>
        </div>
      )}

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-brutal-coral border-3 border-brutal-black p-3 mb-4">
          <div className="flex items-center gap-2 font-bold text-sm mb-1">
            <AlertTriangle className="w-4 h-4" />
            Errors
          </div>
          {errors.map((err, i) => (
            <p key={i} className="text-sm font-mono">{err}</p>
          ))}
        </div>
      )}

      {/* Summary Preview */}
      {summary && (
        <div 
          className={`bg-brutal-white border-3 border-brutal-black p-4 mb-4 cursor-pointer transition-all
            ${isExpanded ? '' : 'max-h-32 overflow-hidden'}`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-4 h-4" />
            <span className="font-bold text-sm">Latest Output</span>
            <span className="text-xs font-mono ml-auto">
              {isExpanded ? '▲ collapse' : '▼ expand'}
            </span>
          </div>
          <p className="text-sm font-mono whitespace-pre-wrap">{summary}</p>
        </div>
      )}

      {/* Artifacts */}
      {artifacts.length > 0 && (
        <div className="mb-4">
          <div className="text-sm font-bold mb-2 flex items-center gap-2">
            <Check className="w-4 h-4" />
            Artifacts ({artifacts.length})
          </div>
          <div className="space-y-2">
            {artifacts.slice(0, 3).map((artifact, i) => (
              <ArtifactChip key={i} artifact={artifact} />
            ))}
            {artifacts.length > 3 && (
              <span className="text-xs font-mono">+{artifacts.length - 3} more</span>
            )}
          </div>
        </div>
      )}

      {/* Run Button */}
      <button
        onClick={onRun}
        disabled={status === 'running'}
        className={`btn-brutal w-full flex items-center justify-center gap-2
          ${status === 'running' ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <Play className="w-5 h-5" />
        {status === 'running' ? 'Running...' : 'Run Now'}
      </button>
    </div>
  )
}

// Artifact display chip
function ArtifactChip({ artifact }) {
  const typeStyles = {
    gmail_draft: { bg: 'bg-brutal-pink', icon: '✉️', label: 'Gmail Draft' },
    notion_page: { bg: 'bg-brutal-white', icon: '📝', label: 'Notion Page' },
    paper: { bg: 'bg-brutal-purple', icon: '📄', label: 'Paper' },
    deadline: { bg: 'bg-brutal-coral', icon: '⏰', label: 'Deadline' },
    plan: { bg: 'bg-brutal-cyan', icon: '📋', label: 'Plan' },
    default: { bg: 'bg-brutal-white', icon: '📎', label: 'Artifact' },
  }

  const style = typeStyles[artifact.type] || typeStyles.default
  const displayTitle = artifact.title || artifact.subject || style.label

  return (
    <div className={`${style.bg} border-2 border-brutal-black px-3 py-2 flex items-center gap-2 text-sm`}>
      <span>{style.icon}</span>
      <span className="font-bold truncate flex-1">{displayTitle}</span>
      {artifact.url && (
        <a 
          href={artifact.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="hover:scale-110 transition-transform"
          onClick={(e) => e.stopPropagation()}
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      )}
    </div>
  )
}