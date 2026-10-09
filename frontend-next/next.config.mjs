/** @type {import('next').NextConfig} */
const BACKEND = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig = {
  reactStrictMode: true,

  // The FastAPI backend only allows localhost:8501 in CORS, and this app runs on
  // :3000. Proxying through Next keeps the backend untouched and avoids CORS.
  async rewrites() {
    return [
      { source: "/api/backend/:path*", destination: `${BACKEND}/:path*` },
    ];
  },
};

export default nextConfig;