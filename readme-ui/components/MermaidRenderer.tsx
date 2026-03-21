"use client";

import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { Maximize2, Activity, Zap } from "lucide-react";

// Initializing outside to prevent re-renders
if (typeof window !== "undefined") {
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    securityLevel: "loose",
    themeVariables: {
      primaryColor: "#1e40af",
      primaryTextColor: "#fff",
      primaryBorderColor: "#3b82f6",
      lineColor: "#60a5fa",
      secondaryColor: "#111827",
      tertiaryColor: "#020203",
      fontFamily: "JetBrains Mono, monospace",
    },
  });
}

export default function MermaidRenderer({ chart }: { chart: string }) {
  const [svg, setSvg] = useState<string>("");
  const [isError, setIsError] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chart) return;

    const renderChart = async () => {
      try {
        setIsError(false);
        // Unique ID for each render to avoid conflicts
        const id = `mermaid-svg-${Math.random().toString(36).substring(2, 9)}`;
        
        // Clean the chart code: Gemini sometimes adds extra backticks
        const cleanChart = chart.replace(/```mermaid/g, "").replace(/```/g, "").trim();

        const { svg: renderedSvg } = await mermaid.render(id, cleanChart);
        
        // Injecting responsiveness: Mermaid default SVGs have fixed width/height
        const responsiveSvg = renderedSvg.replace(
          /<svg/,
          '<svg style="max-width: 100%; height: auto;"'
        );
        
        setSvg(responsiveSvg);
      } catch (err) {
        console.error("❌ Mermaid Render Crash:", err);
        setIsError(true);
      }
    };

    renderChart();
  }, [chart]);

  return (
    <div className="relative group w-full bg-zinc-950/50 backdrop-blur-xl border border-blue-500/20 rounded-[2.5rem] overflow-hidden shadow-2xl shadow-blue-900/10">
      
      {/* 🛰️ Header Component */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-400">
            Architecture_Neural_Map
          </span>
        </div>
        <div className="flex items-center gap-4">
            <Zap className="w-3.5 h-3.5 text-blue-500/50" />
            <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                <Maximize2 className="w-4 h-4 text-zinc-600" />
            </button>
        </div>
      </div>

      {/* 🌳 Render Area */}
      <div className="p-10 flex justify-center items-center min-h-[300px]">
        {isError ? (
          <div className="flex flex-col items-center gap-4 text-center">
            <Activity className="w-8 h-8 text-red-500/50" />
            <p className="text-zinc-500 text-xs font-mono uppercase tracking-widest leading-relaxed">
              System_Failure: Diagram_Complexity_Critical <br />
              <span className="text-blue-500/60 text-[10px]">Attempting_Self_Repair...</span>
            </p>
          </div>
        ) : svg ? (
          <div 
            className="w-full animate-in fade-in zoom-in duration-700"
            dangerouslySetInnerHTML={{ __html: svg }} 
          />
        ) : (
          <div className="flex items-center gap-3">
             <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
             <p className="text-zinc-600 text-[10px] uppercase font-bold tracking-widest">Decoding_Structure...</p>
          </div>
        )}
      </div>

      {/* Futuristic Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.01),rgba(0,255,0,0.005),rgba(0,0,255,0.01))] z-10 bg-[length:100%_2px,3px_100%]" />
    </div>
  );
}