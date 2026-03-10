"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Loader2, Copy, Check, Github, Wand2, Terminal as TerminalIcon, 
  Cpu, Globe, Folder, FileCode, ChevronRight, Edit3, Eye , FileDown
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// 1. Blueprint for Type Safety
interface ReadmeResult {
  status: string;
  markdown: string;
  structure: string[];
  metadata: {
    primary_stack: string;
    detected_frameworks: string[];
    key_dependencies: string[];
    project_type: string;
  };
}

// 2. Sub-Component: Terminal Structure (Hacker Style)
const TerminalStructure = ({ structure = [] }: { structure?: string[] }) => {
  const safeStructure = Array.isArray(structure) ? structure : [];
  return (
    <div className="bg-zinc-950/80 backdrop-blur-2xl border border-blue-500/20 rounded-3xl p-6 font-mono text-[12px] h-full shadow-2xl overflow-hidden relative min-h-[220px]">
      <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-2">
        <TerminalIcon className="w-3.5 h-3.5 text-blue-400" />
        <span className="text-zinc-500 text-[9px] uppercase tracking-widest font-black">Filesystem_Scan_Active</span>
      </div>
      <div className="space-y-1.5 max-h-[160px] overflow-y-auto custom-scrollbar">
        {safeStructure.length > 0 ? (
          safeStructure.map((path, idx) => (
            <div key={idx} className="flex items-center gap-2 group cursor-default">
              <ChevronRight className="w-3 h-3 text-zinc-800" />
              {path.includes("/") || path.includes("\\") ? (
                <Folder className="w-3.5 h-3.5 text-blue-400/60" />
              ) : (
                <FileCode className="w-3.5 h-3.5 text-cyan-400/60" />
              )}
              <span className="text-zinc-500 group-hover:text-zinc-200 transition-colors truncate">{path}</span>
            </div>
          ))
        ) : (
          <p className="text-zinc-700 italic">No structure data detected...</p>
        )}
      </div>
    </div>
  );
};

export default function ReadmeGenerator() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReadmeResult | null>(null);
  const [editableMarkdown, setEditableMarkdown] = useState("");
  const [copied, setCopied] = useState(false);

  // Sync Gemini output with editable state
  useEffect(() => {
    if (result?.markdown) {
      setEditableMarkdown(result.markdown);
    }
  }, [result]);

  const handleGenerate = async () => {
    if (!url) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("http://localhost:8000/generate-readme", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!response.ok) throw new Error("API Offline");
      const data = await response.json();
      setResult(data);
    } catch (err) {
      alert("System Crash: Ensure FastAPI is running on port 8000");
    } finally {
      setLoading(false);
    }
  };

const handleDownload = () => {
  if (!editableMarkdown) return;

  // 1. Create a Blob (Binary Large Object) for the markdown text
  const blob = new Blob([editableMarkdown], { type: "text/markdown" });
  
  // 2. Create a temporary URL for the blob
  const url = URL.createObjectURL(blob);
  
  // 3. Create a hidden 'a' tag and trigger the download
  const link = document.createElement("a");
  link.href = url;
  link.download = "README.md"; // File name set to standard
  document.body.appendChild(link);
  link.click();
  
  // 4. Cleanup: remove the link and revoke the URL
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const cleanMarkdown = editableMarkdown.replace(/\)\s*[\r\n]+\s*\!\[/g, ") ![");
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8 pb-20">
      {/* 🔮 MODULE 1: Search Architecture */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 p-8 rounded-[2.5rem] shadow-2xl"
      >
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Github className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-600" />
            <input
              type="text"
              placeholder="Paste GitHub Repository URL..."
              className="w-full bg-black/50 border border-zinc-800 rounded-2xl pl-14 pr-6 py-4 outline-none focus:ring-2 focus:ring-blue-500/40 text-white transition-all"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading || !url}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 text-white px-10 py-4 rounded-2xl font-black uppercase tracking-widest text-xs flex items-center justify-center gap-3 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
          >
            {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <Wand2 className="w-4 h-4" />}
            {loading ? "Decrypting..." : "Generate Magic"}
          </button>
        </div>
      </motion.div>

      <AnimatePresence mode="wait">
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            {/* 📊 MODULE 2: Intelligence Row (Full Width Top) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
              <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-[2rem] flex flex-col justify-between shadow-xl">
                <h3 className="text-[10px] font-black text-blue-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-2">
                  <Cpu className="w-4 h-4" /> Intelligence_Unit_Analysis
                </h3>
                <div className="grid grid-cols-2 gap-6">
                  <div className="p-6 bg-black/40 rounded-3xl border border-white/5">
                    <p className="text-[10px] text-zinc-600 uppercase font-black mb-2 flex items-center gap-1.5">
                      <Globe className="w-3 h-3" /> Core_Stack
                    </p>
                    <p className="text-xl font-mono font-bold text-white tracking-tighter">
                      {result.metadata?.primary_stack || "Unknown"}
                    </p>
                  </div>
                  <div className="p-6 bg-black/40 rounded-3xl border border-white/5">
                    <p className="text-[10px] text-zinc-600 uppercase font-black mb-3">Registry</p>
                    <div className="flex flex-wrap gap-1.5">
                      {result.metadata?.detected_frameworks.map(fw => (
                        <span key={fw} className="text-[9px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-lg border border-blue-500/20 font-bold uppercase">
                          {fw}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <TerminalStructure structure={result.structure} />
            </div>

            {/* 🚀 MODULE 3: THE SPLIT-SCREEN EDITOR HUB */}
            <div className="w-full bg-zinc-900 border border-zinc-800 rounded-[3rem] overflow-hidden flex flex-col shadow-2xl min-h-[900px]">
              
              {/* Futuristic Toolbar */}
              {/* 🚀 Futuristic Split-Hub Toolbar */}
<div className="bg-zinc-950/70 px-8 py-4 flex justify-between items-center border-b border-white/5 backdrop-blur-2xl sticky top-0 z-30">
  
  {/* LEFT: System Controls & Editor ID */}
  <div className="flex items-center gap-8">
    <div className="flex gap-1.5">
      <div className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
      <div className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
      <div className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
    </div>
    <div className="flex items-center gap-2.5 text-[10px] font-black uppercase tracking-[0.25em] text-blue-400 bg-blue-500/5 px-4 py-2 rounded-xl border border-blue-500/10">
      <Edit3 className="w-3.5 h-3.5" /> Source_Editor
    </div>
  </div>

  {/* RIGHT: Action Cluster (Download + Copy + Preview ID) */}
<div className="flex items-center gap-3">
  
  {/* 🚀 New Download Button */}
  <button 
    onClick={handleDownload}
    className="flex items-center gap-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border border-white/5 active:scale-95 shadow-xl whitespace-nowrap"
  >
    <FileDown className="w-3.5 h-3.5 text-blue-400" />
    <span>Download .md</span>
  </button>

  {/* Existing Copy Button */}
  <button 
    onClick={() => {
      navigator.clipboard.writeText(editableMarkdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }}
    className="flex items-center gap-2.5 bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all shadow-lg shadow-blue-600/20 active:scale-95 whitespace-nowrap"
  >
    {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
    <span>{copied ? "Copied" : "Copy README"}</span>
  </button>

  {/* Preview Label */}
  <div className="flex items-center gap-2.5 text-[10px] font-black uppercase tracking-[0.25em] text-zinc-500 bg-white/5 px-4 py-2.5 rounded-xl border border-white/10">
    <Eye className="w-3.5 h-3.5" /> Visual_Preview
  </div>
</div>
</div>

              {/* Dynamic Split View */}
              <div className="flex flex-1 overflow-hidden h-full">
                
                {/* LEFT: Markdown Input Area */}
                <div className="w-1/2 border-r border-white/5 bg-[#0a0c10] relative">
                  <textarea
                    value={editableMarkdown}
                    onChange={(e) => setEditableMarkdown(e.target.value)}
                    className="w-full h-full p-12 bg-transparent text-zinc-400 font-mono text-[14px] leading-[1.8] resize-none outline-none custom-scrollbar selection:bg-blue-500/30"
                    spellCheck="false"
                  />
                  <div className="absolute bottom-6 left-6 text-[8px] font-mono text-zinc-800 tracking-widest uppercase bg-zinc-900/50 px-3 py-1 rounded">
                    Input_Buffer_Active
                  </div>
                </div>

                {/* RIGHT PANEL: Live Rendered Output */}
<div className="w-1/2 bg-[#0d1117] overflow-y-auto p-10 custom-scrollbar relative border-l border-white/5">
  <div className="absolute top-4 right-6 text-[8px] font-mono text-zinc-700 tracking-[0.2em] uppercase z-20">
    Rendered_GitHub_v4
  </div>
  
  <article className="relative z-10 prose prose-invert max-w-none prose-p:leading-8">
  <ReactMarkdown 
    remarkPlugins={[remarkGfm]}
    components={{
      // 🔥 Sabse bada fix: Paragraph ko Flex container bana do
      p: ({node, ...props}) => {
        // Agar paragraph ke andar sirf images hain, toh use horizontal flow do
        return <p className="flex flex-wrap items-center gap-2 mb-6" {...props} />;
      },
      // 🔥 Images ko inline force karo
      img: ({node, ...props}) => {
        return <img className="inline-block m-0 h-auto max-h-12 rounded-md transition-transform hover:scale-110 shadow-lg" {...props} />;
      },
      // Tables ko professional look do
      table: ({node, ...props}) => (
        <div className="overflow-x-auto my-12 rounded-2xl border border-white/5 shadow-2xl">
          <table className="min-w-full divide-y divide-white/10" {...props} />
        </div>
      ),
    }}
  >
    {cleanMarkdown}
  </ReactMarkdown>
</article>
</div>
              </div>

              {/* Footer Status Bar */}
              <div className="bg-zinc-950/80 px-10 py-3 border-t border-white/5 flex justify-between items-center text-[9px] font-mono text-zinc-600 uppercase tracking-widest">
                <div className="flex gap-6">
                  <span>Encoding: UTF-8</span>
                  <span className="text-blue-900">● AI_Synapse_Connected</span>
                </div>
                <div className="flex gap-4">
                  <span>Lines: {editableMarkdown.split('\n').length}</span>
                  <span>Draft_Mode</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}