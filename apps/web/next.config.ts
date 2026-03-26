import type { NextConfig } from "next";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const normalizedApiBaseUrl = apiBaseUrl.endsWith("/")
  ? apiBaseUrl.slice(0, -1)
  : apiBaseUrl;

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${normalizedApiBaseUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
