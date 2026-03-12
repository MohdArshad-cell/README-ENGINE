"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Loader2, Github, Wand2, Terminal as TerminalIcon, 
  Cpu, Globe, Folder, FileCode, ChevronRight, Edit3, Eye, FileDown, 
  Send, ShieldCheck, Activity, Sparkles, LayoutDashboard, Settings, LogOut, Copy, Check , Waypoints
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast, { Toaster } from "react-hot-toast";
import confetti from "canvas-confetti";

// --- Types ---
interface ReadmeResult {
  markdown: string;
  structure: string[];
  metadata: { primary_stack: string; detected_frameworks: string[]; };
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("readme");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [pushing, setPushing] = useState(false);
  const [result, setResult] = useState<ReadmeResult | null>(null);
  const [editableMarkdown, setEditableMarkdown] = useState("");
  const [isAuthorized, setIsAuthorized] = useState(false);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // 🔐 1. AUTH & TOKEN HANDSHAKE
  useEffect(() => {
    const token = localStorage.getItem("gh_token");
    if (token) setIsAuthorized(true);

    const code = new URLSearchParams(window.location.search).get("code");
    if (code) {
      const authToast = toast.loading("Finalizing GitHub Handshake...");
      fetch(`${BACKEND_URL}/github/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code })
      })
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem("gh_token", data.access_token);
          setIsAuthorized(true);
          toast.success("GitHub Connection Secure", { id: authToast });
          window.history.replaceState({}, document.title, "/dashboard");
        }
      });
    }
  }, [BACKEND_URL]);

  // 📝 2. CORE LOGIC
  const handleGenerate = async () => {
  if (!url) return;
  setLoading(true);
  const genToast = toast.loading("AI Analyzing Repository DNA...");
  try {
    const res = await fetch(`${BACKEND_URL}/generate-readme`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    
    const data = await res.json();
    console.log("Backend Response:", data); // 👈 Debugging ke liye ye line dalo

    // 🔥 FIX: Ensure karo ki hum sirf string nikaal rahe hain
    if (data && data.markdown) {
      setResult(data);
      setEditableMarkdown(typeof data.markdown === 'string' ? data.markdown : JSON.stringify(data.markdown));
      toast.success("Documentation Synthesized!", { id: genToast });
    } else {
      throw new Error("Invalid response format");
    }
  } catch (err) {
    toast.error("System Unreachable or Invalid Data.", { id: genToast });
  } finally {
    setLoading(false);
  }
};

  const handlePush = async () => {
    const token = localStorage.getItem("gh_token");
    setPushing(true);
    const pToast = toast.loading("Pushing Commit to GitHub...");
    try {
      const res = await fetch(`${BACKEND_URL}/github/push`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, repo_url: url, content: editableMarkdown })
      });
      if (res.ok) {
        toast.success("README Updated Live!", { id: pToast });
        confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
      }
    } catch (err) {
      toast.error("Push Rejected.", { id: pToast });
    } finally {
      setPushing(false);
    }
  };


  // dashboard/page.tsx mein handleGenerate ko update karo ya naya function banao
const [mermaidCode, setMermaidCode] = useState("");

const generateDiagram = async () => {
    setLoading(true);
    const dToast = toast.loading("Synthesizing System Architecture...");
    try {
      const res = await fetch(`${BACKEND_URL}/generate-diagram`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      setMermaidCode(data.mermaid_code);
      toast.success("Architecture Map Ready!", { id: dToast });
    } catch (err) {
      toast.error("Neural Mapping Failed.", { id: dToast });
    } finally {
      setLoading(false);
    }
};

  const logout = () => {
    localStorage.removeItem("gh_token");
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 flex font-sans">
      <Toaster position="bottom-right" />

      {/* 🛠️ SIDEBAR: THE CONTROL PANEL */}
      <aside className="w-72 border-r border-white/5 bg-[#050505] p-8 flex flex-col justify-between hidden md:flex">
        <div className="space-y-12">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <TerminalIcon className="w-5 h-5 text-white" />
            </div>
            <span className="font-black tracking-tighter text-lg uppercase italic">ENGINE_v2</span>
          </div>

          <nav className="space-y-2">
            <SidebarLink icon={<LayoutDashboard />} label="README Gen" active={activeTab === "readme"} onClick={() => setActiveTab("readme")} />
            <SidebarLink icon={<Waypoints />} label="Mermaid Docs" active={activeTab === "mermaid"} onClick={() => toast.error("Coming in v2.1!")} />
            <SidebarLink icon={<ShieldCheck />} label="Compliance" active={activeTab === "compliance"} onClick={() => toast.error("Coming in v2.2!")} />
            <SidebarLink icon={<Settings />} label="Settings" active={activeTab === "settings"} onClick={() => {}} />
          </nav>
        </div>

        <button onClick={logout} className="flex items-center gap-3 text-zinc-600 hover:text-red-400 transition-colors text-[10px] font-black uppercase tracking-widest px-4">
          <LogOut className="w-4 h-4" /> Terminate Session
        </button>
      </aside>

      {/* 🚀 MAIN STAGE */}
      <main className="flex-1 overflow-y-auto p-12">
        <header className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-3xl font-black uppercase tracking-tight">System_Dashboard</h1>
            <p className="text-zinc-600 text-xs font-mono tracking-widest mt-1">Status: {isAuthorized ? "AUTHORIZED_GITHUB_SESSION" : "ANONYMOUS_ACCESS"}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 rounded-xl bg-green-500/5 border border-green-500/10 text-[10px] font-black uppercase text-green-500 flex items-center gap-2">
              <Activity className="w-3 h-3" /> API_Stable
            </div>
          </div>
        </header>

        {/* 🔮 MODULE: README GENERATOR (PURANA LOGIC IN NEW SKIN) */}
        <div className="space-y-8">
          <section className="bg-zinc-900/30 border border-white/5 p-8 rounded-[2.5rem] backdrop-blur-xl">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Github className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-700" />
                <input 
                  type="text" 
                  placeholder="Paste GitHub URL..." 
                  className="w-full bg-black/50 border border-white/5 rounded-2xl pl-14 pr-6 py-4 outline-none focus:ring-2 focus:ring-blue-500/40 font-mono text-sm"
                  value={url} onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <button onClick={handleGenerate} disabled={loading || !url} className="bg-blue-600 px-8 rounded-2xl font-black uppercase tracking-widest text-[10px] flex items-center gap-2 hover:bg-blue-500 transition-all">
                {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
                Process_Repo
              </button>
            </div>
          </section>

          {/* Render Result Logic yahan dashboard ke main area mein aayega */}
          {result && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[700px]">
              {/* LEFT: Editor */}
              <div className="bg-[#050505] border border-white/5 rounded-[2rem] flex flex-col overflow-hidden shadow-2xl">
                 <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center">
                    <span className="text-[10px] font-black uppercase tracking-widest text-blue-500">Editor_v2</span>
                    <button onClick={handlePush} disabled={pushing} className="bg-green-600/10 text-green-500 px-4 py-2 rounded-xl text-[9px] font-black uppercase border border-green-500/20 hover:bg-green-600 hover:text-white transition-all">
                      {pushing ? "Pushing..." : "Direct Push"}
                    </button>
                 </div>
                 <textarea value={editableMarkdown} onChange={(e) => setEditableMarkdown(e.target.value)} className="flex-1 p-8 bg-transparent text-zinc-400 font-mono text-xs leading-relaxed outline-none resize-none" />
              </div>

              {/* RIGHT: Live Preview */}
              {/* RIGHT: LIVE RENDER */}
<div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] p-12 overflow-y-auto custom-scrollbar relative shadow-2xl">
  <article className="prose prose-invert max-w-none">
    {/* 🔥 FIX: Ensure editableMarkdown is ALWAYS a string */}
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {String(editableMarkdown || "")} 
    </ReactMarkdown>
  </article>
</div>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

function SidebarLink({ icon, label, active, onClick }: { 
  // ✅ Generic dalo jo bataye ki is element mein className ho sakti hai
  icon: React.ReactElement<{ className?: string }>, 
  label: string, 
  active: boolean, 
  onClick: () => void 
}) {
  return (
    <button 
      onClick={onClick} 
      className={`w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all ${
        active 
          ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" 
          : "text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
      }`}
    >
      {/* Ab TS ko pata hai ki 'className' valid hai */}
      {React.cloneElement(icon, { className: "w-5 h-5" })}
      <span className="text-[10px] font-black uppercase tracking-widest">{label}</span>
    </button>
  );
}