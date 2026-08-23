import "dotenv/config";
import { Pool } from "pg";
import { PrismaPg } from "@prisma/adapter-pg";
import { PrismaClient } from "./generated/prisma/client.js";

export class PrismaPgClient extends PrismaClient {
  constructor() {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error(
        "DATABASE_URL is not set. Load environment variables before creating PrismaPgClient.",
      );
    }
    const pool = new Pool({ connectionString });
    const adapter = new PrismaPg(pool);
    super({ adapter });
  }
}

// --- GLOBAL PG CLIENT (singleton) ---
const globalForPg = globalThis as unknown as { pg: PrismaPgClient };
// Use a getter or initialize later if needed, but since we are exporting the class, NestJS will instantiate it.
// If you still want the singleton:
export const getPg = () => {
  if (!globalForPg.pg) {
    globalForPg.pg = new PrismaPgClient();
  }
  return globalForPg.pg;
};

if (process.env.NODE_ENV !== "production") {
  // globalForPg is assigned when getPg is called
}