import axios, { AxiosInstance } from "axios";

export interface FlexiMongoConfig {
  baseURL: string;
  dbName: string;
  headers?: Record<string, string>;
}

export class FlexiMongoSDK {
  private client: AxiosInstance;
  private dbName: string;

  constructor(config: FlexiMongoConfig) {
    this.dbName = config.dbName;

    this.client = axios.create({
      baseURL: config.baseURL,
      headers: {
        "Content-Type": "application/json",
        ...(config.headers || {}),
      },
    });
  }

  private async request<T>(
    collection: string,
    operationName: string,
    body: any = {},
  ): Promise<T> {
    const response = await this.client.post<T>(
      `/${this.dbName}/${collection}/`,
      body,
      {
        headers: {
          "operation-name": operationName,
        },
      },
    );

    return response.data;
  }

  /* ================= CRUD ================= */

  create<T = any>(collection: string, payload: object) {
    return this.request<T>(collection, "create", { payload });
  }

  find<T = any>(collection: string, documentId: string) {
    return this.request<T>(collection, "find", {
      document_id: documentId,
    });
  }

  findMany<T = any>(collection: string, filters: object = {}) {
    return this.request<T[]>(collection, "find-many", {
      payload: filters,
    });
  }

  update<T = any>(collection: string, documentId: string, payload: object) {
    return this.request<T>(collection, "update", {
      document_id: documentId,
      payload,
    });
  }

  delete<T = any>(collection: string, documentId: string) {
    return this.request<T>(collection, "delete", {
      document_id: documentId,
    });
  }

  /* ============ ADMIN / UTIL ============ */

  clearCollection<T = any>(collection: string) {
    return this.request<T>(collection, "clear-collection");
  }

  dropCollection<T = any>(collection: string) {
    return this.request<T>(collection, "drop-collection");
  }

  count<T = { count: number }>(collection: string, filters = {}) {
    return this.request<T>(collection, "count", {
      payload: filters,
    });
  }

  aggregate<T = any[]>(collection: string, pipeline: object[]) {
    return this.request<T>(collection, "aggregate", {
      pipeline,
    });
  }
}
