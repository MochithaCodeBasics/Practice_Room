const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' },
    ];
  },
  experimental: {
    proxyTimeout: 300000, // 5 minutes (matches backend timeout)
  },
};

module.exports = nextConfig;
