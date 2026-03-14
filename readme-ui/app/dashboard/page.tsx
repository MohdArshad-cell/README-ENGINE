"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Loader2, Github, Terminal as TerminalIcon, 
  Activity, Sparkles, LayoutDashboard, Settings, LogOut, Copy, Waypoints,
  ShieldCheck , FileDown
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import toast, { Toaster } from "react-hot-toast";
import confetti from "canvas-confetti";
import MermaidRenderer from "@/components/MermaidRenderer"; 

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
  const [isPRLoading, setIsPRLoading] = useState(false);
  const [result, setResult] = useState<ReadmeResult | null>(null);
  const [editableMarkdown, setEditableMarkdown] = useState("");
  const [isAuthorized, setIsAuthorized] = useState(false);
  
  // Mermaid States
  const [mermaidCode, setMermaidCode] = useState("");
  const [isDiagramLoading, setIsDiagramLoading] = useState(false);

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
      })
      .catch(() => toast.error("Handshake Failed", { id: authToast }));
    }
  }, [BACKEND_URL]);

  // 📝 2. GENERATE README
  const handleGenerate = async () => {
    if (!url) return;
    setLoading(true);
    setMermaidCode(""); 
    const genToast = toast.loading("AI Analyzing Repository DNA...");
    try {
      const res = await fetch(`${BACKEND_URL}/generate-readme`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      
      const data = await res.json();
      if (data && data.markdown) {
        setResult(data);
        setEditableMarkdown(typeof data.markdown === 'string' ? data.markdown : JSON.stringify(data.markdown));
        toast.success("Documentation Synthesized!", { id: genToast });
      } else {
        throw new Error("Invalid response format");
      }
    } catch (err) {
      toast.error("Generation Failed.", { id: genToast });
    } finally {
      setLoading(false);
    }
  };

  // 📊 3. FETCH MERMAID DIAGRAM
  const fetchDiagram = async () => {
    if (!url) return;
    setIsDiagramLoading(true);
    const dToast = toast.loading("Synthesizing Architecture...");
    try {
      const res = await fetch(`${BACKEND_URL}/generate-diagram`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
      });
      const data = await res.json();
      if (data.mermaid_code) {
        setMermaidCode(data.mermaid_code);
        toast.success("Architecture Mapped!", { id: dToast });
      }
    } catch (err) {
      toast.error("Mapping Failed.", { id: dToast });
    } finally {
      setIsDiagramLoading(false);
    }
  };

  // 📥 4. DOWNLOAD DIAGRAM
  const downloadDiagram = () => {
    const svgElement = document.querySelector("#mermaid-diagram-container svg") as SVGElement;
    if (!svgElement) {
      toast.error("Diagram source not found!");
      return;
    }

    const toastId = toast.loading("Processing Security Clearances...");

    try {
      const serializer = new XMLSerializer();
      let svgData = serializer.serializeToString(svgElement);
      
      if (!svgData.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
        svgData = svgData.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
      }
      
      const base64Data = window.btoa(unescape(encodeURIComponent(svgData)));
      const img = new Image();
      const svgRect = svgElement.getBoundingClientRect();
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = svgRect.width * 2;
      canvas.height = svgRect.height * 2;

      img.onload = () => {
        if (ctx) {
          ctx.fillStyle = "#0d1117"; 
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          
          try {
            const pngUrl = canvas.toDataURL("image/png");
            const downloadLink = document.createElement("a");
            downloadLink.href = pngUrl;
            downloadLink.download = `architecture-map-${Date.now()}.png`;
            downloadLink.click();
            toast.success("Snapshot Saved!", { id: toastId });
          } catch (e) {
            toast.error("Browser security blocked the export.", { id: toastId });
          }
        }
      };
      img.src = `data:image/svg+xml;base64,${base64Data}`;
    } catch (err) {
      toast.error("Serialization failed", { id: toastId });
    }
  };

  // 📤 5. GITHUB DIRECT PUSH
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

  // 🌿 6. GITHUB PULL REQUEST WORKFLOW
  const handleCreatePR = async () => {
    const token = localStorage.getItem("gh_token");
    setIsPRLoading(true);
    const prToast = toast.loading("Initiating Pull Request Workflow...");
    
    try {
      const res = await fetch(`${BACKEND_URL}/github/pull-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, repo_url: url, content: editableMarkdown })
      });
      
      const data = await res.json();
      if (data.status === "success") {
        toast.success("PR Created Successfully!", { id: prToast });
        window.open(data.pr_url, "_blank"); 
      } else {
        throw new Error(data.message);
      }
    } catch (err) {
      toast.error("PR Failed. Check permissions.", { id: prToast });
    } finally {
      setIsPRLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("gh_token");
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 flex font-sans">
      <Toaster position="bottom-right" />

      {/* 🛠️ SIDEBAR */}
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
            <SidebarLink 
              icon={<Waypoints />} 
              label="Mermaid Docs" 
              active={activeTab === "mermaid"} 
              onClick={() => {
                setActiveTab("mermaid");
                if (result && !mermaidCode) fetchDiagram();
              }} 
            />
            <SidebarLink icon={<ShieldCheck />} label="Compliance" active={activeTab === "compliance"} onClick={() => toast.error("v2.2 Restricted")} />
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
            <p className="text-zinc-600 text-xs font-mono tracking-widest mt-1">Status: {isAuthorized ? "AUTHORIZED_SESSION" : "ANONYMOUS_ACCESS"}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 rounded-xl bg-green-500/5 border border-green-500/10 text-[10px] font-black uppercase text-green-500 flex items-center gap-2">
              <Activity className="w-3 h-3" /> API_Stable
            </div>
          </div>
        </header>

        {/* 🔮 URL INPUT */}
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

          {/* 🚀 DYNAMIC CONTENT AREA */}
          {result && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
              
              {/* TABS */}
              <div className="flex gap-6 border-b border-white/5 pb-4">
                <button 
                  onClick={() => setActiveTab("readme")}
                  className={`text-[10px] font-black uppercase tracking-widest pb-2 transition-all ${activeTab === "readme" ? "border-b-2 border-blue-500 text-blue-500" : "text-zinc-500 hover:text-zinc-300"}`}
                >
                  README_ENGINE
                </button>
                <button 
                  onClick={() => {
                    setActiveTab("mermaid");
                    if (!mermaidCode) fetchDiagram();
                  }}
                  className={`text-[10px] font-black uppercase tracking-widest pb-2 transition-all ${activeTab === "mermaid" ? "border-b-2 border-blue-500 text-blue-500" : "text-zinc-500 hover:text-zinc-300"}`}
                >
                  SYSTEM_ARCHITECTURE
                </button>
              </div>

              <AnimatePresence mode="wait">
                {activeTab === "readme" ? (
                  <motion.div key="readme" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[700px]">
                    
                    {/* Editor Side */}
                    <div className="bg-[#050505] border border-white/5 rounded-[2rem] flex flex-col overflow-hidden">
                      <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center bg-black/50">
                        <span className="text-[10px] font-black uppercase tracking-widest text-blue-500">Editor_v2</span>
                        <div className="flex gap-2">
                          {/* Pull Request Button */}
                          <button 
                            onClick={handleCreatePR} 
                            disabled={isPRLoading} 
                            className="bg-blue-600/10 text-blue-400 px-4 py-2 rounded-xl text-[9px] font-black uppercase border border-blue-500/20 hover:bg-blue-600 hover:text-white transition-all disabled:opacity-50"
                          >
                            {isPRLoading ? "Opening PR..." : "Create Pull Request"}
                          </button>
                          {/* Direct Push Button */}
                          <button 
                            onClick={handlePush} 
                            disabled={pushing} 
                            className="bg-green-600/10 text-green-500 px-4 py-2 rounded-xl text-[9px] font-black uppercase border border-green-500/20 hover:bg-green-600 hover:text-white transition-all disabled:opacity-50"
                          >
                            {pushing ? "Pushing..." : "Direct Push"}
                          </button>
                        </div>
                      </div>
                      <textarea value={editableMarkdown} onChange={(e) => setEditableMarkdown(e.target.value)} className="flex-1 p-8 bg-transparent text-zinc-400 font-mono text-xs leading-relaxed outline-none resize-none custom-scrollbar" />
                    </div>

                    {/* Preview Side */}
                    <div className="bg-[#0d1117] border border-white/5 rounded-[2.5rem] p-12 overflow-y-auto custom-scrollbar relative">
                      <article className="prose prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {String(editableMarkdown || "")} 
                        </ReactMarkdown>
                      </article>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div key="mermaid" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} className="bg-[#050505] border border-white/5 rounded-[2.5rem] p-12 min-h-[600px] flex flex-col items-center justify-center relative">
                    {isDiagramLoading ? (
                      <div className="flex flex-col items-center gap-6">
                        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
                        <p className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 animate-pulse">Mapping_Infrastructure...</p>
                      </div>
                    ) : mermaidCode ? (
                      <div className="w-full h-full flex flex-col items-center">
                        <div className="w-full flex justify-between items-center mb-8">
                          <span className="text-[10px] font-black uppercase tracking-widest text-zinc-500">Live_Architecture_Graph</span>
                          <div className="flex gap-3">
                            <button 
                              onClick={() => { navigator.clipboard.writeText(mermaidCode); toast.success("Code Copied!"); }} 
                              className="p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-all text-zinc-400 hover:text-white"
                              title="Copy Mermaid Code"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                            
                            <button 
                              onClick={downloadDiagram}
                              className="p-3 bg-blue-600/20 rounded-xl hover:bg-blue-600/40 border border-blue-500/30 transition-all text-blue-400 hover:text-white flex items-center gap-2"
                              title="Download as PNG"
                            >
                              <FileDown className="w-4 h-4" />
                              <span className="text-[9px] font-black uppercase tracking-wider">Download_PNG</span>
                            </button>
                          </div>
                        </div>

                        <div className="w-full bg-[#0d1117]/50 rounded-3xl border border-white/5 p-8">
                          <div id="mermaid-diagram-container" className="w-full flex justify-center">
                            <MermaidRenderer chart={mermaidCode} />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <button onClick={fetchDiagram} className="bg-blue-600 px-8 py-4 rounded-2xl font-black uppercase tracking-widest text-[10px]">
                        Initialize_Scan
                      </button>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}

// --- Helper Component ---
function SidebarLink({ icon, label, active, onClick }: { 
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
      {React.cloneElement(icon, { className: "w-5 h-5" })}
      <span className="text-[10px] font-black uppercase tracking-widest">{label}</span>
    </button>
  );
}