const path = require('path');

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
      { source: '/api/:path*', destination: 'http://localhost:3001/api/:path*' },
    ];
  },
};

module.exports = nextConfig;
