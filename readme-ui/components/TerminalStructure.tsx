"use client";

import React from "react";
import { motion } from "framer-motion";
import { Folder, FileCode, ChevronRight, Terminal } from "lucide-react";

interface Props {
  // "?" lagane se ye optional ho gaya, billionaire safety first!
  structure?: string[]; 
}

export default function TerminalStructure({ structure = [] }: Props) {
  // Agar structure null ya undefined ho, toh empty array use hogi
  
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.04 },
    },
  };

  const item = {
    hidden: { x: -15, opacity: 0 },
    show: { x: 0, opacity: 1 },
  };

  return (
    <div className="bg-zinc-950/60 backdrop-blur-2xl border border-blue-500/20 rounded-3xl p-6 font-mono text-[13px] relative overflow-hidden group shadow-2xl shadow-blue-900/10">
      {/* Futuristic Header */}
      <div className="flex items-center justify-between mb-5 border-b border-white/5 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1 bg-blue-500/10 rounded-md">
            <Terminal className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <span className="text-zinc-500 text-[10px] uppercase tracking-[0.2em] font-black">
            System_Manifest_v1.4
          </span>
        </div>
        <div className="flex gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-zinc-800" />
          <div className="w-1.5 h-1.5 rounded-full bg-zinc-800" />
        </div>
      </div>

      {/* The Animated Tree */}
      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar"
      >
        {/* Safety Check: Agar structure khali hai toh empty state dikhao */}
        {structure.length === 0 ? (
          <p className="text-zinc-600 italic animate-pulse">Waiting for metadata stream...</p>
        ) : (
          structure.map((path, index) => {
            // Logic to detect folders vs files
            const isFolder = path.includes("\\") || path.includes("/");
            
            return (
              <motion.div 
                key={index} 
                variants={item}
                className="flex items-center gap-2.5 group/line cursor-default py-0.5"
              >
                <ChevronRight className="w-3 h-3 text-zinc-800 group-hover/line:text-blue-500 transition-colors" />
                {isFolder ? (
                  <Folder className="w-4 h-4 text-blue-400/60 group-hover/line:text-blue-400" />
                ) : (
                  <FileCode className="w-4 h-4 text-cyan-400/60 group-hover/line:text-cyan-400" />
                )}
                <span className="text-zinc-500 group-hover/line:text-zinc-100 transition-colors truncate">
                  {path}
                </span>
              </motion.div>
            );
          })
        )}
      </motion.div>

      {/* Cyberpunk Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.02),rgba(0,255,0,0.01),rgba(0,0,255,0.02))] z-10 bg-[length:100%_2px,3px_100%]" />
    </div>
  );
}