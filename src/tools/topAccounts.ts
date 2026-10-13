import { z } from "zod";
import type { McpServer, RegisteredTool } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { Deps } from "../client.js";
import { UNTRUSTED_NOTICE } from "../shape.js";
import { cursorArg, limitArg, orderArg, page, run } from "./util.js";

export function registerTopAccounts(server: McpServer, deps: Deps): RegisteredTool {
  return server.registerTool(
    "top_accounts",
    {
      title: "Top accounts",
      description:
        "X accounts ranked by standing: how much other accounts engage with them. Free on Pay-as-you-go and Grow plans. Standing measures attention, not accuracy: track is how an account's calls have done, and is null when it has never opened a position. Pass a handle to the calls tool to see its positions.",
      inputSchema: {
        order: orderArg.describe("desc (default) ranks the highest standing first."),
        limit: limitArg(200),
        cursor: cursorArg,
      },
      outputSchema: {
        notice: z.string(),
        items: z.array(z.record(z.unknown())),
        nextCursor: z.string().nullable(),
        hasMore: z.boolean(),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async (args) =>
      run(deps, async () => {
        const response = await deps.v3.get("/v3/people/accounts", {
          order: args.order,
          limit: args.limit,
          cursor: args.cursor,
        });
        const { items, nextCursor, hasMore } = page(response, "accounts");
        return { notice: UNTRUSTED_NOTICE, items, nextCursor, hasMore };
      }),
  );
}
