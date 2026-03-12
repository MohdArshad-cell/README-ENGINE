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
    if (!chart || !ref.current) return;

    // 🚀 FRONTEND AGGRESSIVE CLEANER (V6)
    const cleanChart = chart
      // 1. Fix Labeled Arrows: A --> Text --> B to A -->|Text| B
      .replace(/-->\s*(.*?)\s*-->/g, "-->|$1| ")
      // 2. Flatten Subgraph Titles: Remove nested quotes and brackets
      .replace(/subgraph\s+"?(.*?)"?/g, (m, g) => `subgraph "${g.replace(/[()"]/g, "").trim()}"`)
      // 3. Universal Label Flattener: No double quotes, no parentheses
      .replace(/(\[|\(|\{)(.*?)(\]|\)|\})/g, (m, bO, content, bC) => {
        const flatContent = content.replace(/[()"]/g, "").trim().replace(/\s+/g, " ");
        return `${bO}"${flatContent}"${bC}`;
      })
      // 4. Broken arrow fix
      .replace(/ --\s/g, " --> ");

    // Unique ID generation
    const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;

    const renderDiagram = async () => {
      try {
        // Clear previous content
        const { svg } = await mermaid.render(id, cleanChart);
        setSvg(svg);
      } catch (err) {
        console.error("Mermaid Render Error:", err);
        // Fallback UI if rendering still fails
        setSvg(`
          <div class="flex flex-col items-center p-4 text-center">
            <p class="text-red-500 text-[10px] font-black uppercase tracking-widest mb-2">Render_Engine_Failure</p>
            <p class="text-zinc-600 text-[9px] font-mono leading-tight">Syntax too complex for real-time visualization.<br/>Check 'Editor' for raw Mermaid code.</p>
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
      className="w-full overflow-x-auto flex justify-center bg-[#0d1117]/50 p-8 rounded-[2rem] border border-white/5 shadow-inner"
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
}