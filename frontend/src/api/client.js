import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Workflow Output Contract:
 * {
 *   ok: boolean,
 *   workflow: string,
 *   summary: string,
 *   artifacts: array,
 *   errors: array,
 * }
 */

export const api = {
  // ===== DASHBOARD =====
  async getDashboard() {
    try {
      const response = await axiosInstance.get("/dashboard");
      return response.data;
    } catch (err) {
      console.warn("Backend not available, using mock data");
      return getMockDashboard();
    }
  },

  // ===== RUN WORKFLOW =====
  async runWorkflow(workflowId) {
    const endpointMap = {
      "research-log": "/workflows/research-log/run",
      "advisor-update": "/workflows/advisor-update/run",
      "paper-scout": "/workflows/paper-scout/run",
      "deadline-guardian": "/workflows/deadline-guardian/run",
      "week-planner": "/workflows/week-planner/run",
    };

    try {
      const response = await axiosInstance.post(endpointMap[workflowId]);
      return normalizeWorkflowResponse(response.data);
    } catch (err) {
      console.warn(`Workflow ${workflowId} failed, using mock`);
      return getMockWorkflowResult(workflowId);
    }
  },

  // ===== SETTINGS =====
  async getSettings() {
    try {
      const response = await axiosInstance.get("/settings");
      return response.data;
    } catch (err) {
      return getDefaultSettings();
    }
  },

  async saveSettings(settings) {
    const response = await axiosInstance.post("/settings", settings);
    return response.data;
  },
};

// ===== NORMALIZE BACKEND RESPONSE TO UI STATE =====
function normalizeWorkflowResponse(data) {
  return {
    status: data.ok ? "success" : "error",
    summary: data.summary || "No summary provided",
    artifacts: data.artifacts || [],
    errors: data.errors || [],
    workflow: data.workflow,
    timestamp: new Date().toISOString(),
  };
}

// ===== MOCK DATA FOR DEVELOPMENT =====
function getMockDashboard() {
  return {
    stats: {
      codingHours: 14.5,
      commits: 27,
      upcomingDeadlines: 4,
      papersFound: 6,
    },
    workflows: {
      "research-log": {
        ok: true,
        workflow: "research_log",
        status: "success",
        lastRun: "2024-01-15T10:30:00Z",
        summary:
          "Logged 14.5 hours across 3 projects:\n• pitch-tipping: 9h\n• ara-hackathon: 4h\n• coursework: 1.5h",
        artifacts: [
          { type: "notion_page", id: "abc123", title: "Research Log - Week 3" },
        ],
        errors: [],
      },
      "advisor-update": {
        ok: true,
        workflow: "advisor_update",
        status: "success",
        lastRun: "2024-01-12T17:00:00Z",
        summary:
          "Gmail draft created with 5 progress points and 2 blockers.",
        artifacts: [
          {
            type: "gmail_draft",
            id: "draft_xyz",
            subject: "Weekly Update - Jan 12",
          },
        ],
        errors: [],
      },
      "paper-scout": {
        ok: true,
        workflow: "paper_scout",
        status: "idle",
        lastRun: null,
        summary: null,
        artifacts: [],
        errors: [],
      },
      "deadline-guardian": {
        ok: true,
        workflow: "deadline_guardian",
        status: "success",
        lastRun: "2024-01-15T09:00:00Z",
        summary:
          "⚠️ 2 deadlines within 48 hours:\n• CS 601 HW3 - Tomorrow 11:59 PM\n• Proposal draft - Wed 5 PM",
        artifacts: [
          { type: "deadline", title: "CS 601 HW3", due: "2024-01-16T23:59:00Z" },
          {
            type: "deadline",
            title: "Proposal draft",
            due: "2024-01-17T17:00:00Z",
          },
        ],
        errors: [],
      },
      "week-planner": {
        ok: true,
        workflow: "week_planner",
        status: "idle",
        lastRun: "2024-01-14T18:00:00Z",
        summary: "Week plan generated with 3 priorities and 4 focus blocks.",
        artifacts: [],
        errors: [],
      },
    },
  };
}

function getMockWorkflowResult(workflowId) {
  const mocks = {
    "research-log": {
      ok: true,
      workflow: "research_log",
      summary:
        "Logged 8.5 hours of coding activity.\n\nBreakdown:\n• pitch-tipping: 5.5h (model training)\n• ara-hackathon: 2h (frontend)\n• misc: 1h",
      artifacts: [
        { type: "notion_page", id: "new123", title: "Research Log - Week 3" },
      ],
      errors: [],
    },
    "advisor-update": {
      ok: true,
      workflow: "advisor_update",
      summary:
        'Gmail draft created: "Weekly Update - Jan 15"\n\n**Progress:**\n• Completed data pipeline refactor\n• Fixed 3 bugs in model training loop\n• Started documentation for API\n\n**Blockers:**\n• Waiting on GPU cluster access\n• Need clarification on eval metrics',
      artifacts: [
        {
          type: "gmail_draft",
          id: "draft_abc",
          subject: "Weekly Update - Jan 15",
        },
      ],
      errors: [],
    },
    "paper-scout": {
      ok: true,
      workflow: "paper_scout",
      summary:
        'Found 3 relevant papers:\n\n1. **"Scaling Laws for Neural LMs"**\n   Relevance: 95% • Kaplan et al.\n\n2. **"Constitutional AI"**\n   Relevance: 88% • Anthropic\n\n3. **"Tree of Thoughts"**\n   Relevance: 82% • Yao et al.',
      artifacts: [
        {
          type: "paper",
          title: "Scaling Laws for Neural LMs",
          url: "https://arxiv.org/abs/2001.08361",
          relevance: 0.95,
        },
        {
          type: "paper",
          title: "Constitutional AI",
          url: "https://arxiv.org/abs/2212.08073",
          relevance: 0.88,
        },
        {
          type: "paper",
          title: "Tree of Thoughts",
          url: "https://arxiv.org/abs/2305.10601",
          relevance: 0.82,
        },
      ],
      errors: [],
    },
    "deadline-guardian": {
      ok: true,
      workflow: "deadline_guardian",
      summary:
        "🚨 **3 upcoming deadlines detected:**\n\n• CS 601 Assignment 3 → Tomorrow 11:59 PM\n• Research proposal draft → Wednesday 5 PM\n• Lab meeting slides → Thursday 2 PM\n\n✅ Telegram reminder sent.",
      artifacts: [
        {
          type: "deadline",
          title: "CS 601 Assignment 3",
          due: "2024-01-16T23:59:00Z",
          source: "canvas",
        },
        {
          type: "deadline",
          title: "Research proposal draft",
          due: "2024-01-17T17:00:00Z",
          source: "calendar",
        },
        {
          type: "deadline",
          title: "Lab meeting slides",
          due: "2024-01-18T14:00:00Z",
          source: "todoist",
        },
      ],
      errors: [],
    },
    "week-planner": {
      ok: true,
      workflow: "week_planner",
      summary:
        "📋 **Week Plan Generated**\n\n**Priority 1:** Finish CS 601 assignment\n**Priority 2:** Address advisor feedback on draft\n**Priority 3:** Read 2 papers from scout list\n\n**Focus Blocks Scheduled:**\n• Mon 9-12: Deep work (assignment)\n• Tue 2-5: Writing (proposal)\n• Wed 10-12: Reading\n• Thu 9-11: Slides prep",
      artifacts: [
        {
          type: "plan",
          priorities: ["Finish CS 601", "Advisor feedback", "Read papers"],
        },
      ],
      errors: [],
    },
  };

  return normalizeWorkflowResponse(
    mocks[workflowId] || {
      ok: true,
      workflow: workflowId,
      summary: "Workflow completed successfully.",
      artifacts: [],
      errors: [],
    }
  );
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