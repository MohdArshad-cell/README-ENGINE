"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, useScroll, useTransform } from "framer-motion";
import { 
  Github, Wand2, Zap, ShieldCheck, Sparkles, ChevronRight, 
  Terminal, Code2, Waypoints, Cpu, Globe, Lock, Check 
} from "lucide-react";
import toast, { Toaster } from "react-hot-toast";

/**
 * 🛰️ HELPER COMPONENT: BENTO CARD
 */
function BentoCard({ icon, title, desc, badge }: { 
  icon: React.ReactNode, 
  title: string, 
  desc: string, 
  badge: string 
}) {
  return (
    <div className="p-10 rounded-[3rem] bg-zinc-900/20 border border-white/5 backdrop-blur-sm group hover:bg-zinc-900/40 hover:border-blue-500/30 transition-all">
      <div className="w-14 h-14 bg-zinc-900 rounded-2xl flex items-center justify-center text-blue-500 mb-8 border border-white/5 shadow-inner group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <div className="flex items-center gap-3 mb-4">
        <h3 className="font-black uppercase tracking-widest text-sm text-white">{title}</h3>
        <span className="text-[8px] bg-blue-500/10 text-blue-500 px-2 py-0.5 rounded-md font-black uppercase tracking-widest border border-blue-500/20">{badge}</span>
      </div>
      <p className="text-zinc-500 text-sm leading-relaxed font-medium">{desc}</p>
    </div>
  );
}

/**
 * 🧬 HELPER COMPONENT: STEP CARD
 */
function StepCard({ num, title, desc }: { num: string, title: string, desc: string }) {
  return (
    <div className="relative p-10 bg-zinc-900/10 border border-white/5 rounded-3xl group hover:border-blue-500/40 transition-all">
      <span className="absolute -top-6 -left-6 text-6xl font-black text-white/5 group-hover:text-blue-500/10 transition-colors tracking-tighter">{num}</span>
      <h3 className="text-sm font-black uppercase tracking-[0.3em] mb-4 text-blue-400 relative z-10">{title}</h3>
      <p className="text-zinc-500 text-xs leading-relaxed relative z-10">{desc}</p>
    </div>
  );
}

/**
 * 🚀 MAIN COMPONENT: FUTURISTIC LANDING
 */
export default function FuturisticLanding() {
  const router = useRouter();
  const GITHUB_CLIENT_ID = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID;
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, 80]);

  useEffect(() => {
    // 1. Agar token pehle se hai, toh seedha dashboard
    const token = localStorage.getItem("gh_token");
    if (token) {
      router.push("/dashboard");
      return;
    }

    // 2. Agar URL mein code aaya hai, toh use Dashboard par transfer karo
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    
    if (code) {
      // Isse fetch karne ki zaroorat landing page par nahi hai
      // Dashboard asali kaam karega
      router.push(`/dashboard?code=${code}`);
    }
  }, [router]);

  const handleLogin = () => {
  if (!GITHUB_CLIENT_ID) {
    alert("Bhai, Client ID abhi bhi undefined hai! .env check karo.");
    return;
  }
  window.location.href = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=repo`;
};

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 selection:bg-blue-500/30 overflow-x-hidden font-sans">
      <Toaster position="bottom-right" reverseOrder={false} />
      
      {/* 🌌 THE GRID: Cyberpunk Background */}
      <div className="fixed inset-0 z-0 opacity-20" 
           style={{ backgroundImage: `radial-gradient(#1e40af 0.5px, transparent 0.5px), radial-gradient(#1e40af 0.5px, #020203 0.5px)`, backgroundSize: '40px 40px' }} />
      <div className="fixed inset-0 z-0 bg-gradient-to-b from-transparent via-[#020203]/80 to-[#020203]" />

      {/* 🛰️ ELITE NAVIGATION */}
      <nav className="max-w-7xl mx-auto px-8 py-10 flex justify-between items-center relative z-50">
        <div className="flex items-center gap-4 group cursor-pointer">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(37,99,235,0.4)] group-hover:rotate-12 transition-transform">
            <Terminal className="w-6 h-6 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-black tracking-tighter text-2xl uppercase leading-none">README_ENGINE</span>
            <span className="text-[8px] font-mono text-blue-500 uppercase tracking-[0.4em] font-bold">Lucknow_Deployment_v2</span>
          </div>
        </div>
        <button 
          onClick={handleLogin} 
          className="group flex items-center gap-3 bg-white/5 backdrop-blur-md border border-white/10 px-6 py-2.5 rounded-full hover:bg-white/10 transition-all text-[10px] font-bold uppercase tracking-widest"
        >
          <Github className="w-4 h-4 text-white" />
          <span>Access Systems</span>
        </button>
      </nav>

      {/* 🔥 HERO SECTION */}
      <main className="max-w-7xl mx-auto px-8 pt-20 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center mb-40">
          <motion.div initial={{ opacity: 0, x: -50 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8 }}>
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-[10px] font-black uppercase tracking-[0.3em] text-blue-400 mb-8 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
              <Cpu className="w-4 h-4 animate-pulse" /> Neural_Network_Active
            </div>
            
            <h1 className="text-7xl md:text-9xl font-black tracking-tighter leading-[0.85] mb-10">
              CODE IS <br /> 
              <span className="bg-gradient-to-r from-blue-500 to-cyan-400 bg-clip-text text-transparent">ALIVE.</span>
            </h1>
            
            <p className="text-zinc-500 text-lg md:text-xl font-medium mb-12 max-w-lg leading-relaxed border-l-2 border-blue-500/30 pl-6">
              Dont just write Markdown. Orchestrate your projects identity. 
              Our engine decodes your architecture and commits directly to your source.
            </p>

            <div className="flex flex-col sm:flex-row gap-6">
              <button 
                onClick={handleLogin}
                className="relative overflow-hidden group bg-blue-600 px-12 py-5 rounded-2xl font-black uppercase tracking-widest text-[11px] transition-all hover:shadow-[0_0_40px_rgba(37,99,235,0.4)]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500" />
                <span className="flex items-center justify-center gap-3">
                  Initiate Handshake <ChevronRight className="w-4 h-4" />
                </span>
              </button>
              <div className="flex items-center gap-4 px-8 py-5 border border-white/5 rounded-2xl text-[10px] uppercase font-bold text-zinc-600 tracking-widest whitespace-nowrap">
                <Globe className="w-4 h-4" /> 12.4k Commits Made
              </div>
            </div>
          </motion.div>

          {/* DYNAMIC TERMINAL PREVIEW */}
          <motion.div style={{ y: y1 }} className="hidden lg:block relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-[2.5rem] blur opacity-20 group-hover:opacity-40 transition duration-1000" />
            <div className="relative bg-black border border-white/10 rounded-[2.5rem] p-4 shadow-2xl">
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 mb-4">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-zinc-800" />
                  <div className="w-3 h-3 rounded-full bg-zinc-800" />
                </div>
                <div className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Process: analyze_repository.sh</div>
              </div>
              <div className="space-y-3 font-mono text-sm p-6 overflow-hidden h-[400px]">
                <p className="text-blue-500"> arshad@engine:~$ <span className="text-white">analyze --target ./my-app</span></p>
                <p className="text-zinc-500">[SYSTEM] Cloning target repository...</p>
                <p className="text-zinc-500">[SCAN] Detected Framework: <span className="text-cyan-400 font-bold">Next.js 15</span></p>
                <p className="text-zinc-500">[SCAN] Detected Engine: <span className="text-cyan-400 font-bold">FastAPI</span></p>
                <p className="text-green-500">✓ Metadata extracted successfully.</p>
                <p className="text-zinc-500">[AI] Generating elite technical README...</p>
                <div className="mt-8 p-4 bg-zinc-900/50 rounded-xl border border-white/5">
                  <p className="text-zinc-400"># Project_Alpha</p>
                  <p className="text-zinc-600">The high-concurrency engine for...</p>
                  <p className="text-zinc-600 mt-2">## System_Architecture</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* 📊 SOCIAL PROOF / STATS BAR */}
        <div className="border-y border-white/5 bg-zinc-900/10 py-12 backdrop-blur-sm mb-40">
          <div className="max-w-7xl mx-auto px-8 flex flex-wrap justify-around gap-12 opacity-50 grayscale hover:grayscale-0 transition-all">
            <div className="flex items-center gap-2 font-black uppercase tracking-tighter text-sm"> <Github className="w-5 h-5"/> GitHub_Open_API</div>
            <div className="flex items-center gap-2 font-black uppercase tracking-tighter text-sm"> <Zap className="w-5 h-5 text-yellow-500"/> Vercel_Edge</div>
            <div className="flex items-center gap-2 font-black uppercase tracking-tighter text-sm"> <Sparkles className="w-5 h-5 text-blue-500"/> Google_Gemini</div>
            <div className="flex items-center gap-2 font-black uppercase tracking-tighter text-sm"> <ShieldCheck className="w-5 h-5 text-green-500"/> OCI_Certified</div>
          </div>
        </div>

        {/* 🧩 THE BENTO GRID (Features) */}
        <section className="mb-40 relative z-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <BentoCard 
              icon={<Waypoints className="w-6 h-6" />}
              title="Mermaid_Logic"
              desc="Automatic system architecture flowcharts generated via AI. Visualize your project logic in seconds."
              badge="Coming Soon"
            />
            <BentoCard 
              icon={<Lock className="w-6 h-6" />}
              title="Secure_OAuth"
              desc="Bank-grade security for your tokens. We never store your code—only push the results."
              badge="Standard"
            />
            <BentoCard 
              icon={<Code2 className="w-6 h-6" />}
              title="Multi_Stack"
              desc="Whether it's Python, Java, or TypeScript, the engine adapts to your project's primary DNA."
              badge="Neural"
            />
          </div>
        </section>

        {/* 🧬 THE PROCESS SECTION */}
        <section className="py-40 relative">
          <div className="text-center mb-24">
            <h2 className="text-4xl font-black uppercase tracking-widest mb-4 italic text-white">The_Process</h2>
            <div className="h-1 w-20 bg-blue-600 mx-auto rounded-full" />
          </div>

          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 px-8">
            <StepCard num="01" title="Initialize_Sync" desc="Connect your repository via Secure OAuth. Our engine performs a read-only metadata handshake." />
            <StepCard num="02" title="Neural_Synthesis" desc="Gemini-2.5 scans file signatures and directory structures to map your project's DNA." />
            <StepCard num="03" title="Atomic_Commit" desc="A production-ready README is pushed directly to your main branch. Zero copy-pasting required." />
          </div>
        </section>

        {/* 💰 PRICING SECTION */}
        <section className="py-40 bg-zinc-950/50 rounded-[4rem] border border-white/5 mb-20">
          <div className="max-w-5xl mx-auto px-8 grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Basic Tier */}
            <div className="p-12 rounded-[3rem] border border-white/5 bg-black hover:border-zinc-700 transition-all">
              <h4 className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-6">Standard_Unit</h4>
              <div className="text-4xl font-black mb-8 text-white">$0 <span className="text-xs text-zinc-600 font-medium lowercase">/ forever</span></div>
              <ul className="space-y-4 mb-12 text-xs text-zinc-400 font-mono uppercase tracking-widest">
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Unlimited Public Repos</li>
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Basic AI Scan</li>
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Direct GitHub Push</li>
              </ul>
              <button className="w-full py-4 rounded-xl border border-white/10 text-[10px] font-black uppercase tracking-widest hover:bg-white/5 transition-all text-white">Deploy_Free</button>
            </div>

            {/* Pro Tier */}
            <div className="p-12 rounded-[3rem] border border-blue-500/30 bg-blue-600/5 relative overflow-hidden group">
              <div className="absolute top-0 right-0 px-6 py-2 bg-blue-600 text-[8px] font-black uppercase tracking-widest rounded-bl-2xl text-white">Elite_Selection</div>
              <h4 className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-6">Enterprise_Node</h4>
              <div className="text-4xl font-black mb-8 text-white">$9 <span className="text-xs text-zinc-600 font-medium lowercase">/ month</span></div>
              <ul className="space-y-4 mb-12 text-xs text-zinc-300 font-mono uppercase tracking-widest">
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Private Repository Access</li>
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Mermaid.js Diagrams</li>
                <li className="flex items-center gap-3"><Check className="w-4 h-4 text-blue-500"/> Custom AI Templates</li>
              </ul>
              <button className="w-full py-4 rounded-xl bg-blue-600 text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-all shadow-[0_0_30px_rgba(37,99,235,0.3)] text-white">Acquire_Pro_License</button>
            </div>
          </div>
        </section>

        {/* 📋 ELITE FOOTER */}
        <footer className="border-t border-white/5 py-20 px-8 text-center">
          <div className="flex flex-col items-center gap-6">
            <div className="flex items-center gap-2">
              <Terminal className="w-5 h-5 text-blue-500" />
              <span className="font-black tracking-widest text-xs uppercase italic text-white">README_ENGINE // INTERNAL_ACCESS_ONLY</span>
            </div>
            <p className="text-[9px] font-mono text-zinc-700 uppercase tracking-[0.5em]">Developed_by_Arshad // Unit_Lucknow_2026</p>
          </div>
        </footer>
      </main>
    </div>
  );
}