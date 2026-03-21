"use client";

import React from "react";
import { motion } from "framer-motion";
import { Github, ExternalLink, ShieldCheck } from "lucide-react";

interface Props {
  className?: string;
}

const GitHubInstallButton: React.FC<Props> = ({ className }) => {
  // ✅ PRO TIP: '/installations/new' lagane se user seedha install screen par jata hai
  const INSTALLATION_URL = "https://github.com/apps/readme-engine-pro/installations/new";

  return (
    <div className={`relative group ${className}`}>
      {/* 🌌 External Glow Effect */}
      <div className="absolute -inset-1 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl blur opacity-25 group-hover:opacity-60 transition duration-1000 group-hover:duration-200" />
      
      <motion.a
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98 }}
        href={INSTALLATION_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="relative flex flex-col items-center justify-center gap-1 bg-zinc-950 border border-green-500/30 px-10 py-5 rounded-2xl transition-all hover:border-green-400 group/btn"
      >
        <div className="flex items-center gap-4">
          <div className="p-2 bg-green-500/10 rounded-lg group-hover/btn:bg-green-500/20 transition-colors">
            <Github className="w-6 h-6 text-green-400" />
          </div>
          
          <div className="flex flex-col items-start">
            <span className="text-white text-sm font-black uppercase tracking-widest flex items-center gap-2">
              Install_On_GitHub <ExternalLink className="w-3 h-3 opacity-50" />
            </span>
            <span className="text-[9px] text-zinc-500 font-bold uppercase tracking-tighter flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-green-500/50" /> Secure_Handshake_v2
            </span>
          </div>
        </div>

        {/* Animated Scanline on the button */}
        <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
          <div className="w-full h-[1px] bg-green-500/20 absolute top-0 left-0 animate-scanline-fast" />
        </div>
      </motion.a>
      
      {/* 🏷️ Tooltip/Hint */}
      <p className="mt-3 text-[8px] text-zinc-600 font-mono uppercase tracking-[0.3em] text-center opacity-0 group-hover:opacity-100 transition-opacity">
        Authorizing_Read_Write_Permissions
      </p>
    </div>
  );
};

export default GitHubInstallButton;