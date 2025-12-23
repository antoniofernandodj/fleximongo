import axios, { AxiosInstance } from "axios";

export interface FlexiMongoConfig {
  baseURL: string;
  databaseName: string;
  collectionName: string;
  headers?: Record<string, string>;
}

class Collection {
  private client: AxiosInstance;
  constructor(
    private readonly baseURL: string,
    private readonly databaseName: string,
    private readonly collectionName: string,
    headers?: Record<string, string>,
  ) {
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        "Content-Type": "application/json",
        ...(headers || {}),
      },
    });
  }

  private async request<T>(operationName: string, body: any = {}): Promise<T> {
    const response = await this.client.post<T>(
      `/${this.databaseName}/${this.collectionName}/`,
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

  create<T = any>(payload: object) {
    return this.request<T>("create", { payload });
  }

  find<T = any>(documentId: string) {
    return this.request<T>("find", { document_id: documentId });
  }

  findMany<T = any>(filters: object = {}) {
    return this.request<T[]>("find-many", { payload: filters });
  }

  update<T = any>(documentId: string, payload: object) {
    return this.request<T>("update", { document_id: documentId, payload });
  }

  delete<T = any>(documentId: string) {
    return this.request<T>("delete", { document_id: documentId });
  }

  /* ============ ADMIN / UTIL ============ */

  clearCollection<T = any>() {
    return this.request<T>("clear-collection");
  }

  dropCollection<T = any>() {
    return this.request<T>("drop-collection");
  }

  count<T = { count: number }>(filters = {}) {
    return this.request<T>("count", {
      payload: filters,
    });
  }

  aggregate<T = any[]>(pipeline: object[]) {
    return this.request<T>("aggregate", {
      pipeline,
    });
  }
}

class Database {
  static collections = new Map<string, Collection>();

  collection(name: string): Collection {
    if (!Database.collections.has(name)) {
      Database.collections.set(
        name,
        new Collection(this.baseURL, this.databaseName, name, this.headers),
      );
    }
    return Database.collections.get(name)!;
  }

  constructor(
    private readonly baseURL: string,
    private readonly databaseName: string,
    private readonly headers?: Record<string, string>,
  ) {
    this.baseURL = baseURL;
    this.databaseName = databaseName;

    return new Proxy(this, {
      get: (target, prop, receiver) => {
        if (typeof prop === "symbol") {
          return Reflect.get(target, prop, receiver);
        }

        // permite métodos reais da classe
        if (prop in target) {
          return Reflect.get(target, prop, receiver);
        }

        return (
          Database.collections.get(prop) ??
          Database.collections
            .set(
              prop,
              new Collection(this.baseURL, this.databaseName, String(prop)),
            )
            .get(prop)
        );

        return;
      },
    });
  }
}

export class FlexiMongoSDK {
  private readonly databases = new Map<string, Database>();

  constructor(
    private readonly baseURL: string,
    private readonly headers?: Record<string, string>,
  ) {
    return new Proxy(this, {
      get: (target, prop, receiver) => {
        if (typeof prop === "symbol") {
          return Reflect.get(target, prop, receiver);
        }

        // métodos reais da classe
        if (prop in target) {
          return Reflect.get(target, prop, receiver);
        }

        return this.db(String(prop));
      },
    });
  }

  /** API explícita (tipada) */
  db(name: string): Database {
    if (!this.databases.has(name)) {
      this.databases.set(name, new Database(this.baseURL, name, this.headers));
    }
    return this.databases.get(name)!;
  }
}
