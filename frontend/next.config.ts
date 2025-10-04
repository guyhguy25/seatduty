import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'imagecache.365scores.com',
        port: '',
        pathname: '/image/upload/**',
      },
    ],
  },
  output: 'standalone',
};

export default nextConfig;
