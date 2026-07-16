import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    const noStore = [
      {
        key: "Cache-Control",
        value: "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0",
      },
    ];

    return [
      { source: "/", headers: noStore },
      { source: "/questions.json", headers: noStore },
    ];
  },
};

export default nextConfig;
