/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@cognitive-os/ui", "@cognitive-os/shared-types"],
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
