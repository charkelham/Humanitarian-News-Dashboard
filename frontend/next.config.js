/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://humanitarian-news-dashboard-production.up.railway.app',
  },
}

module.exports = nextConfig
