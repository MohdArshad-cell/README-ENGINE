import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// 🛰️ CUSTOM METADATA (Billionaire-tier branding)
export const metadata: Metadata = {
  title: "README_ENGINE // V2",
  description: "AI-Powered Technical Documentation & Architecture Mapper",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // 🌍 YE DONO TAGS HONA ZAROORI HAI (Root Layout Rule)
    <html lang="en" className="dark">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#020203] text-zinc-100`}>
        {/* Saare pages (Hero, Dashboard) isi children mein load honge */}
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}