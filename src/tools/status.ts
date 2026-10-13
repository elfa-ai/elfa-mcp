import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { Deps } from "../client.js";
import { describeError } from "../errors.js";
import { run } from "./util.js";

const REPORTED = [
  "tier",
  "status",
  "isExpired",
  "expiresAt",
  "billingMode",
  "usage",
  "limits",
  "remainingRequests",
  "dailyRequestLimit",
  "monthlyRequestLimit",
  "requestsPerMinute",
  "allowOverage",
  "bonusCredits",
  "depositCredits",
  "spendCapCredits",
  "athenaEnabled",
  "scopes",
] as const;

function summarise(data: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const field of REPORTED) {
    if (data[field] !== undefined) out[field] = data[field];
  }
  return out;
}

export function registerStatus(server: McpServer, deps: Deps): void {
  server.registerTool(
    "api_status",
    {
      title: "API key status",
      description:
        "Check the Elfa API key tier, credit usage and remaining requests, and confirm the API is reachable. Free. Call this first when a request fails with an auth or credit error. historyFrom is the earliest time, in unix seconds, the events, market and calls tools read on this plan.",
      inputSchema: {},
      outputSchema: {
        reachable: z.boolean(),
        key: z.record(z.unknown()).nullable(),
        historyFrom: z.number().nullable(),
        problem: z.string().nullable(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async () =>
      run(deps, async () => {
        const [ping, status, v3Status] = await Promise.allSettled([
          deps.sdk.ping(),
          deps.sdk.getApiKeyStatus(),
          deps.v3.get("/v3/key-status"),
        ]);
        const historyFrom =
          v3Status.status === "fulfilled" ? v3Status.value.historyFrom : undefined;

        return {
          reachable: ping.status === "fulfilled",
          key:
            status.status === "fulfilled"
              ? summarise(status.value.data as unknown as Record<string, unknown>)
              : null,
          historyFrom: typeof historyFrom === "number" ? historyFrom : null,
          problem:
            status.status === "rejected"
              ? describeError(status.reason)
              : null,
        };
      }),
  );
}
