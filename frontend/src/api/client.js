import axios from "axios";

// ===== USE VITE_API_URL - NO HARDCODED LOCALHOST =====
const BASE_URL = import.meta.env.VITE_API_URL || "/api";

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Backend Dashboard Contract (LOCKED):
 * {
 *   "generatedAt": "2026-04-19T15:30:00",
 *   "stats": { codingHours, commits, upcomingDeadlines, papersFound },
 *   "workflows": { "research-log": {...}, ... },
 *   "recentArtifacts": []
 * }
 *
 * Backend Workflow Run Contract (LOCKED):
 * {
 *   "ok": true,
 *   "workflow": "advisor_update",
 *   "summary": "...",
 *   "artifacts": [],
 *   "errors": [],
 *   "data": {},
 *   "generated_at": "..."
 * }
 */

// ===== WORKFLOW IDS (must match backend exactly) =====
export const WORKFLOW_IDS = {
  RESEARCH_LOG: "research-log",
  ADVISOR_UPDATE: "advisor-update",
  PAPER_SCOUT: "paper-scout",
  DEADLINE_GUARDIAN: "deadline-guardian",
  WEEK_PLANNER: "week-planner",
};

export const api = {
  // ===== GET DASHBOARD =====
  async getDashboard() {
    try {
      const response = await axiosInstance.get("/dashboard");
      return validateDashboardResponse(response.data);
    } catch (err) {
      console.warn("Backend not available, using mock data:", err.message);
      return getMockDashboard();
    }
  },

  // ===== RUN WORKFLOW =====
  async runWorkflow(workflowId) {
    const validIds = Object.values(WORKFLOW_IDS);
    if (!validIds.includes(workflowId)) {
      throw new Error(`Invalid workflow ID: ${workflowId}`);
    }

    try {
      const response = await axiosInstance.post(`/workflows/${workflowId}/run`);
      return validateWorkflowResponse(response.data);
    } catch (err) {
      console.warn(`Workflow ${workflowId} failed:`, err.message);
      // Return error shape matching contract
      return {
        ok: false,
        workflow: workflowId,
        summary: `Failed to run workflow: ${err.message}`,
        artifacts: [],
        errors: [err.message],
        data: {},
        generated_at: new Date().toISOString(),
      };
    }
  },

  // ===== SETTINGS =====
  async getSettings() {
    try {
      const response = await axiosInstance.get("/settings");
      return response.data;
    } catch (err) {
      console.warn("Settings not available, using defaults");
      return getDefaultSettings();
    }
  },

  async saveSettings(settings) {
    const response = await axiosInstance.post("/settings", settings);
    return response.data;
  },
};

// ===== VALIDATION HELPERS =====

function validateDashboardResponse(data) {
  // Ensure response matches locked contract shape
  return {
    generatedAt: data.generatedAt || new Date().toISOString(),
    stats: {
      codingHours: data.stats?.codingHours ?? 0,
      commits: data.stats?.commits ?? 0,
      upcomingDeadlines: data.stats?.upcomingDeadlines ?? 0,
      papersFound: data.stats?.papersFound ?? 0,
    },
    workflows: {
      "research-log": validateWorkflowState(data.workflows?.["research-log"]),
      "advisor-update": validateWorkflowState(data.workflows?.["advisor-update"]),
      "paper-scout": validateWorkflowState(data.workflows?.["paper-scout"]),
      "deadline-guardian": validateWorkflowState(data.workflows?.["deadline-guardian"]),
      "week-planner": validateWorkflowState(data.workflows?.["week-planner"]),
    },
    recentArtifacts: data.recentArtifacts || [],
  };
}

function validateWorkflowState(workflow) {
  return {
    status: workflow?.status || "idle",
    lastRun: workflow?.lastRun || "",
    summary: workflow?.summary || "",
    artifacts: workflow?.artifacts || [],
    errors: workflow?.errors || [],
  };
}

function validateWorkflowResponse(data) {
  return {
    ok: data.ok ?? false,
    workflow: data.workflow || "unknown",
    summary: data.summary || "",
    artifacts: data.artifacts || [],
    errors: data.errors || [],
    data: data.data || {},
    generated_at: data.generated_at || new Date().toISOString(),
  };
}

// ===== MOCK DATA (matches production contract exactly) =====

function getMockDashboard() {
  return {
    generatedAt: new Date().toISOString(),
    stats: {
      codingHours: 14.5,
      commits: 27,
      upcomingDeadlines: 4,
      papersFound: 6,
    },
    workflows: {
      "research-log": {
        status: "success",
        lastRun: "2026-04-19T10:30:00Z",
        summary:
          "Logged 14.5 hours across 3 projects:\n• pitch-tipping: 9h\n• ara-hackathon: 4h\n• coursework: 1.5h",
        artifacts: [
          { type: "notion_page", id: "abc123", title: "Research Log - Week 3" },
        ],
        errors: [],
      },
      "advisor-update": {
        status: "success",
        lastRun: "2026-04-18T17:00:00Z",
        summary: "Gmail draft created with 5 progress points and 2 blockers.",
        artifacts: [
          {
            type: "gmail_draft",
            id: "draft_xyz",
            subject: "Weekly Update - Apr 18",
          },
        ],
        errors: [],
      },
      "paper-scout": {
        status: "idle",
        lastRun: "",
        summary: "",
        artifacts: [],
        errors: [],
      },
      "deadline-guardian": {
        status: "success",
        lastRun: "2026-04-19T09:00:00Z",
        summary:
          "⚠️ 4 deadlines within 48 hours:\n• CS 601 HW3 - Tomorrow 11:59 PM\n• Proposal draft - Wed 5 PM",
        artifacts: [
          { type: "deadline", title: "CS 601 HW3", due: "2026-04-20T23:59:00Z" },
          { type: "deadline", title: "Proposal draft", due: "2026-04-21T17:00:00Z" },
        ],
        errors: [],
      },
      "week-planner": {
        status: "idle",
        lastRun: "2026-04-14T18:00:00Z",
        summary: "Week plan generated with 3 priorities and 4 focus blocks.",
        artifacts: [],
        errors: [],
      },
    },
    recentArtifacts: [
      { type: "gmail_draft", title: "Weekly Update - Apr 18", workflow: "advisor-update" },
      { type: "notion_page", title: "Research Log - Week 3", workflow: "research-log" },
    ],
  };
}

function getDefaultSettings() {
  return {
    keywords: "machine learning, neural networks, transformers",
    repoName: "pitch-tipping",
    deliveryChannel: "telegram",
    writeDestination: "notion",
    canvasUrl: "",
    canvasConnected: false,
  };
}