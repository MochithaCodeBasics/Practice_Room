const path = require('path');
const backendBaseUrl = process.env.BACKEND_URL || 'http://localhost:3001';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    return [
      {
        source: '/api/auth/:path*',
        destination: '/api/auth/:path*',
      },
      { source: '/api/:path*', destination: `${backendBaseUrl}/api/:path*` },
    ];
  },
};

module.exports = nextConfig;
