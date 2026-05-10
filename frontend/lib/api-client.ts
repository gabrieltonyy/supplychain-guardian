import type {
  WorkflowRunResponse,
  WorkflowRunsListResponse,
  WorkflowDetailResponse,
  TimelineResponse,
  ReplayResponse,
  AnalyticsSummaryResponse,
  RiskDistributionResponse,
  SupplierRankingsResponse,
} from "./api-types";
import {
  AnalyticsSummaryResponseSchema,
  ReplayResponseSchema,
  RiskDistributionResponseSchema,
  SupplierRankingsResponseSchema,
  TimelineResponseSchema,
  WorkflowDetailResponseSchema,
  WorkflowRunResponseSchema,
  WorkflowRunsListResponseSchema,
} from "./api-types";
import type { ZodTypeAny } from "zod";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(
    endpoint: string,
    schema: ZodTypeAny,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail?.message || errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    const data = await response.json();
    return schema.parse(data) as T;
  }

  // POST /api/v1/db-workflow/run/{supplier_id}
  async runWorkflow(supplierId: string): Promise<WorkflowRunResponse> {
    return this.fetch<WorkflowRunResponse>(
      `/api/v1/db-workflow/run/${supplierId}`,
      WorkflowRunResponseSchema,
      {
        method: "POST",
      }
    );
  }

  // GET /api/v1/db-workflow/runs
  async listWorkflowRuns(limit: number = 50): Promise<WorkflowRunsListResponse> {
    return this.fetch<WorkflowRunsListResponse>(
      `/api/v1/db-workflow/runs?limit=${limit}`,
      WorkflowRunsListResponseSchema
    );
  }

  // GET /api/v1/db-workflow/{workflow_id}
  async getWorkflowRun(workflowId: string): Promise<WorkflowDetailResponse> {
    return this.fetch<WorkflowDetailResponse>(
      `/api/v1/db-workflow/${workflowId}`,
      WorkflowDetailResponseSchema
    );
  }

  // GET /api/v1/db-workflow/{workflow_id}/timeline
  async getWorkflowTimeline(workflowId: string): Promise<TimelineResponse> {
    return this.fetch<TimelineResponse>(
      `/api/v1/db-workflow/${workflowId}/timeline`,
      TimelineResponseSchema
    );
  }

  // GET /api/v1/db-workflow/{workflow_id}/replay
  async getWorkflowReplay(workflowId: string): Promise<ReplayResponse> {
    return this.fetch<ReplayResponse>(
      `/api/v1/db-workflow/${workflowId}/replay`,
      ReplayResponseSchema
    );
  }

  // GET /api/v1/db-workflow/analytics/summary
  async getAnalyticsSummary(): Promise<AnalyticsSummaryResponse> {
    return this.fetch<AnalyticsSummaryResponse>(
      `/api/v1/db-workflow/analytics/summary`,
      AnalyticsSummaryResponseSchema
    );
  }

  // GET /api/v1/db-workflow/analytics/risk-distribution
  async getRiskDistribution(): Promise<RiskDistributionResponse> {
    return this.fetch<RiskDistributionResponse>(
      `/api/v1/db-workflow/analytics/risk-distribution`,
      RiskDistributionResponseSchema
    );
  }

  // GET /api/v1/db-workflow/analytics/supplier-rankings
  async getSupplierRankings(limit: number = 10): Promise<SupplierRankingsResponse> {
    return this.fetch<SupplierRankingsResponse>(
      `/api/v1/db-workflow/analytics/supplier-rankings?limit=${limit}`,
      SupplierRankingsResponseSchema
    );
  }
}

export const apiClient = new ApiClient();
