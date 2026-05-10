import type {
  WorkflowRunResponse,
  WorkflowRunsListResponse,
  WorkflowDetailResponse,
  TimelineResponse,
  ReplayResponse,
  RFQActionsResponse,
  RFQDetailResponse,
  RFQListResponse,
  AnalyticsSummaryResponse,
  RiskDistributionResponse,
  SupplierRankingsResponse,
} from "./api-types";
import {
  AnalyticsSummaryResponseSchema,
  ReplayResponseSchema,
  RFQActionsResponseSchema,
  RFQDetailResponseSchema,
  RFQListResponseSchema,
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

  // GET /api/v1/rfqs
  async listRFQs(params?: {
    search?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<RFQListResponse> {
    const query = new URLSearchParams();

    if (params?.search) query.set("search", params.search);
    if (params?.status && params.status !== "ALL") {
      query.set("status", params.status);
    }
    query.set("limit", String(params?.limit ?? 100));
    query.set("offset", String(params?.offset ?? 0));

    return this.fetch<RFQListResponse>(
      `/api/v1/rfqs?${query.toString()}`,
      RFQListResponseSchema
    );
  }

  async approveRFQ(rfqId: string, note?: string): Promise<RFQDetailResponse> {
    return this.fetch<RFQDetailResponse>(
      `/api/v1/rfqs/${encodeURIComponent(rfqId)}/approve`,
      RFQDetailResponseSchema,
      {
        method: "POST",
        body: JSON.stringify({ note }),
      }
    );
  }

  async requestRFQReview(rfqId: string, note?: string): Promise<RFQDetailResponse> {
    return this.fetch<RFQDetailResponse>(
      `/api/v1/rfqs/${encodeURIComponent(rfqId)}/request-review`,
      RFQDetailResponseSchema,
      {
        method: "POST",
        body: JSON.stringify({ note }),
      }
    );
  }

  async rejectRFQ(rfqId: string, note?: string): Promise<RFQDetailResponse> {
    return this.fetch<RFQDetailResponse>(
      `/api/v1/rfqs/${encodeURIComponent(rfqId)}/reject`,
      RFQDetailResponseSchema,
      {
        method: "POST",
        body: JSON.stringify({ note }),
      }
    );
  }

  async listRFQActions(rfqId: string): Promise<RFQActionsResponse> {
    return this.fetch<RFQActionsResponse>(
      `/api/v1/rfqs/${encodeURIComponent(rfqId)}/actions`,
      RFQActionsResponseSchema
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
