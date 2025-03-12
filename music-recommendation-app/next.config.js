/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['i.scdn.co', 'mosaic.scdn.co', 'firebasestorage.googleapis.com'],
  },
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /node_modules\/@firebase\/auth\/node_modules\/undici\/lib\/web\/fetch\/util\.js$/,
      use: 'null-loader',
      include: /node_modules/,
    });

    return config;
  },

  modularizeImports: {
    'firebase': {
      transform: false,
    }
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig