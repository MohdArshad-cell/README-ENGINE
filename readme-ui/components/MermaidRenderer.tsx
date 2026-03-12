"use client";
import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

// 🔧 MERMAID CONFIG
mermaid.initialize({
  startOnLoad: false, // Manual render use kar rahe hain
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
    if (!chart || !ref.current) return;

    const renderDiagram = async () => {
      // 🚀 FRONTEND SHIELD: Final sanitization before passing to Mermaid
      let cleanChart = chart
      .replace(/--\|/g, "-->|") // 🚀 Fixing the Lexical Error directly
  .replace(/--\s/g, " --> ")
        .replace(/\\"/g, '"')         // Fix escaped quotes
        .replace(/""/g, '"')          // Fix double quotes
        .replace(/\]"\]/g, '"]')       // Fix common bracket hallucination
        .replace(/-->\s*(.*?)\s*-->/g, "-->|$1| ") // Fix labeled arrows
        .replace(/ --\s/g, " --> ");   // Fix broken arrows

      // Ensure it starts with graph TD
      cleanChart = cleanChart.trim();
      if (!cleanChart.startsWith("graph TD") && !cleanChart.startsWith("flowchart TD")) {
        cleanChart = "graph TD\n" + cleanChart.replace(/graph TD|flowchart TD/g, "").trim();
      }

      // Unique ID for every render
      const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;

      try {
        const { svg: renderedSvg } = await mermaid.render(id, cleanChart);
        setSvg(renderedSvg);
      } catch (err) {
        console.error("Mermaid Render Error:", err);
        // Stylish Fallback UI
        setSvg(`
          <div class="flex flex-col items-center justify-center p-12 border border-red-500/20 bg-red-500/5 rounded-[2rem]">
            <p class="text-red-500 text-[10px] font-black uppercase tracking-[0.3em] mb-2">Synthesis_Failed</p>
            <p class="text-zinc-500 text-[9px] font-mono leading-relaxed">
              Syntax error in generated graph. <br/> 
              Try clicking 'Initialize Scan' again.
            </p>
          </div>
        `);
      }
    };

    renderDiagram();
  }, [chart]);

  return (
    <div 
      id="mermaid-diagram-container"
      ref={ref} 
      className="w-full overflow-x-auto flex justify-center bg-[#0d1117]/50 p-12 rounded-[2.5rem] border border-white/5 shadow-2xl transition-all duration-500"
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
}