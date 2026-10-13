import { z } from "zod";
import type { McpServer, RegisteredTool } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { Deps } from "../client.js";
import { cursorArg, limitArg, page, run } from "./util.js";

export function registerEntities(server: McpServer, deps: Deps): RegisteredTool {
  return server.registerTool(
    "entities",
    {
      title: "Entities",
      description:
        "Turn a ticker, $cashtag, name, @handle, contract address, CoinGecko id, FIGI or CIK into the entity id that events and calls take. Free on Pay-as-you-go and Grow plans. It matches exactly, it is not a search: a prefix or a misspelling returns nothing. A ticker is not unique, so take the first row and check its name, or narrow with entityType. Every form of an asset resolves to one family id: WBTC and cbBTC are Bitcoin. Resolve once and reuse the id.",
      inputSchema: {
        q: z
          .string()
          .min(1)
          .max(128)
          .describe('What you hold, for example "btc", "$SOL", "@VitalikButerin" or a contract address.'),
        entityType: z
          .array(z.enum(["token", "equity", "project", "person", "organisation"]))
          .optional()
          .describe("Narrow the match to these kinds. Omit to match every kind."),
        limit: limitArg(200),
        cursor: cursorArg,
      },
      outputSchema: {
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
        const response = await deps.v3.get("/v3/entities", {
          q: args.q,
          entityType: args.entityType,
          limit: args.limit,
          cursor: args.cursor,
        });
        const { items, nextCursor, hasMore } = page(response, "entities");
        return { items, nextCursor, hasMore };
      }),
  );
}
