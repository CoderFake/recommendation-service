/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      domains: ['i.scdn.co', 'mosaic.scdn.co', 'firebasestorage.googleapis.com'],
    },
    eslint: {
      dirs: ['src'],
    },
    experimental: {
      serverActions: true,
    },
  }
  
  module.exports = nextConfig