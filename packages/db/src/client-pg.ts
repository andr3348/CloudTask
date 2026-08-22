import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "./generated/prisma/client.js";

const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error(
    "DATABASE_URL is not set. Load environment variables before creating PrismaPgClient.",
  );
}

const adapter = new PrismaPg({ connectionString });

export class PrismaPgClient extends PrismaClient {
  constructor() {
    super({ adapter });
  }
}

// --- GLOBAL PG CLIENT (singleton) ---
const globalForPg = globalThis as unknown as { pg: PrismaPgClient };
export const pg = globalForPg.pg ?? new PrismaPgClient();

if (process.env.NODE_ENV !== "production") globalForPg.pg = pg;