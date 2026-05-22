import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import vue from "@vitejs/plugin-vue";
import { build } from "vite";

const frontendRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));

await build({
  root: frontendRoot,
  configFile: false,
  plugins: [vue()],
  server: {
    port: 5173,
  },
});
