/**
 * Run `build` or `dev` with `SKIP_ENV_VALIDATION` to skip env validation. This is especially useful
 * for Docker builds.
 */
import "./src/env.js";

/** @type {import("next").NextConfig} */
const config = {
  env: {
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
  },
  serverRuntimeConfig: {
    // Will only be available on the server side
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
  },
};

export default config;
