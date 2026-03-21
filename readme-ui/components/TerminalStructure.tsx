"use client";

import React from "react";
import { motion } from "framer-motion";
import { Folder, FileCode, ChevronRight, Terminal, Hash } from "lucide-react";

interface Props {
  structure?: string[]; 
}

export default function TerminalStructure({ structure = [] }: Props) {
  
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.03 },
    },
  };

  const item = {
    hidden: { x: -10, opacity: 0 },
    show: { x: 0, opacity: 1 },
  };

  return (
    <div className="bg-zinc-950/80 backdrop-blur-xl border border-blue-500/30 rounded-3xl p-6 font-mono text-[13px] relative overflow-hidden group shadow-2xl shadow-blue-500/5">
      
      {/* 🛰️ System Header */}
      <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="absolute -inset-1 bg-blue-500/20 blur-sm rounded-full animate-pulse" />
            <Terminal className="w-4 h-4 text-blue-400 relative" />
          </div>
          <div className="flex flex-col">
            <span className="text-zinc-100 text-[11px] font-black uppercase tracking-widest">
              Directory_Intelligence
            </span>
            <span className="text-[9px] text-blue-500/60 font-bold uppercase tracking-tighter">
              Ready_For_Neural_Scan
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Hash className="w-3 h-3 text-zinc-800" />
          <div className="w-2 h-2 rounded-full bg-blue-500/20" />
        </div>
      </div>

      {/* 🌳 The Intelligence Tree */}
      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-1.5 max-h-[450px] overflow-y-auto pr-3 custom-scrollbar scrollbar-hide"
      >
        {structure.length === 0 ? (
          <div className="py-10 text-center">
             <p className="text-zinc-700 italic text-xs animate-pulse tracking-widest"> 🛰️ Awaiting Metadata Stream...</p>
          </div>
        ) : (
          structure.map((path, index) => {
            // ✅ IMPROVED LOGIC: 
            // 1. Agar path '/' par khatam ho raha hai toh folder hai.
            // 2. Agar path ke end mein '.' nahi hai (extension missing), toh mostly folder hai.
            const isFolder = path.endsWith("/") || path.endsWith("\\") || !path.split('/').pop()?.includes('.');
            
            // Clean path name for display (sirf aakhri part dikhana behtar hota hai, par tune full manga hai)
            const parts = path.split(/[/\\]/);
            const fileName = parts[parts.length - 1] || parts[parts.length - 2];

            return (
              <motion.div 
                key={index} 
                variants={item}
                className="flex items-center gap-3 group/line cursor-pointer py-1 px-2 rounded-lg hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center justify-center w-4">
                   <ChevronRight className="w-3 h-3 text-zinc-800 group-hover/line:text-blue-500 group-hover/line:translate-x-0.5 transition-all" />
                </div>
                
                {isFolder ? (
                  <Folder className="w-4 h-4 text-blue-500/40 group-hover/line:text-blue-400 transition-colors" />
                ) : (
                  <FileCode className="w-4 h-4 text-cyan-500/40 group-hover/line:text-cyan-400 transition-colors" />
                )}
                
                <span className="text-zinc-500 group-hover/line:text-zinc-200 transition-colors truncate tracking-tight font-medium">
                  {path}
                </span>

                {/* Optional: Deep Scan Badge */}
                {!isFolder && (
                   <div className="ml-auto opacity-0 group-hover/line:opacity-100 transition-opacity">
                      <span className="text-[8px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/20">SCANNED</span>
                   </div>
                )}
              </motion.div>
            );
          })
        )}
      </motion.div>

      {/* Futuristic Scanline Effect */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-blue-500/[0.02] to-transparent h-1/2 w-full animate-scanline z-20" />
    </div>
  );
}