"use client";
import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({ startOnLoad: false, theme: "dark" });

export default function MermaidRenderer({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState("");

  useEffect(() => {
    if (!chart || !ref.current) return;

    const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;

    mermaid.render(id, chart)
      .then(({ svg }) => setSvg(svg))
      .catch((err) => {
        console.error("Render Error:", err);
        setSvg("<p class='text-zinc-500 text-[10px]'>Diagram too complex. Refreshing...</p>");
      });
  }, [chart]);

  return (
    <div 
      ref={ref} 
      className="w-full flex justify-center bg-[#0d1117]/50 p-8 rounded-[2rem] border border-white/5"
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
}