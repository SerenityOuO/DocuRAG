import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import { createServer } from "vite";

const frontendRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));

const server = await createServer({
  root: frontendRoot,
  configFile: false,
  plugins: [vue()],
  server: {
    port: 5173,
  },
});

await server.listen();
server.printUrls();
