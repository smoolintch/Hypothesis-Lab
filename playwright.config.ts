import { defineConfig, devices } from "@playwright/test";

const apiPort = process.env.PLAYWRIGHT_API_PORT ?? "8000";
const webPort = process.env.PLAYWRIGHT_WEB_PORT ?? "3100";
const webBaseUrl = `http://127.0.0.1:${webPort}`;
const apiBaseUrl = `http://127.0.0.1:${apiPort}/api`;
const sqliteDbPath =
  process.env.PLAYWRIGHT_SQLITE_DB_PATH ?? "/tmp/hypothesis-lab-playwright.db";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: webBaseUrl,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
  webServer: [
    {
      command:
        `rm -f "${sqliteDbPath}" && ` +
        `cd "services/api" && ` +
        `DATABASE_URL="sqlite+pysqlite:///${sqliteDbPath}" ` +
        `DEFAULT_USER_ID="00000000-0000-0000-0000-000000000001" ` +
        `APP_USER_MODE="single_user" ` +
        `uv run alembic upgrade head && ` +
        `DATABASE_URL="sqlite+pysqlite:///${sqliteDbPath}" ` +
        `DEFAULT_USER_ID="00000000-0000-0000-0000-000000000001" ` +
        `APP_USER_MODE="single_user" ` +
        `API_HOST="127.0.0.1" ` +
        `API_PORT="${apiPort}" ` +
        `uv run uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      url: `${apiBaseUrl.replace("/api", "")}/openapi.json`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command:
        `NEXT_PUBLIC_API_BASE_URL="${apiBaseUrl}" ` +
        `corepack pnpm --filter @hypothesis-lab/web build && ` +
        `NEXT_PUBLIC_API_BASE_URL="${apiBaseUrl}" ` +
        `corepack pnpm --filter @hypothesis-lab/web start --hostname 127.0.0.1 --port ${webPort}`,
      url: `${webBaseUrl}/strategy-cards/new`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
