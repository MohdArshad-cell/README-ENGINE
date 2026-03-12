"use client";
import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

// 🔧 MERMAID CONFIG
mermaid.initialize({
  startOnLoad: true,
  theme: "dark",
  securityLevel: "loose",
  themeVariables: {
    primaryColor: "#3b82f6",
    lineColor: "#60a5fa",
    fontFamily: "Inter, sans-serif",
  }
});

export default function MermaidRenderer({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState("");

  useEffect(() => {
    if (chart && ref.current) {
      // 🚀 THE FRONTEND GUARD: Render hone se pehle cleaning
      // 1. Labels ke andar se dangerous () hatao aur unhe quotes "" mein wrap karo
      // 2. Broken arrows '--' ko '-->' mein badlo
      const cleanChart = chart
        .replace(/\[(.*?)\]/g, (m, g) => `["${g.replace(/[()]/g, " ")}"]`) 
        .replace(/\{(.*?)\}/g, (m, g) => `{"${g.replace(/[()]/g, " ")}"}`)
        .replace(/\((.*?)\)/g, (m, g) => `("${g.replace(/[()]/g, " ")}")`)
        .replace(/ --\s/g, " --> "); 

      // Unique ID for every render
      const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;
      
      try {
        mermaid.render(id, cleanChart).then(({ svg }) => {
          setSvg(svg);
        }).catch((err) => {
          console.error("Mermaid Render Error:", err);
        });
      } catch (err) {
        console.error("Mermaid Syntax Crash:", err);
      }
    }
  }, [chart]);

  return (
    <div 
      id="mermaid-diagram-container" // 👈 Ye ID download function ke liye zaroori hai
      ref={ref} 
      className="w-full overflow-x-auto flex justify-center bg-[#0d1117]/50 p-8 rounded-[2rem] border border-white/5 shadow-inner"
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
}