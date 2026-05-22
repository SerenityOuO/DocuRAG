import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { preview } from "vite";

const frontendRoot = resolve(fileURLToPath(new URL("..", import.meta.url)));

const server = await preview({
  root: frontendRoot,
  configFile: false,
  preview: {
    port: 4173,
  },
});

server.printUrls();
