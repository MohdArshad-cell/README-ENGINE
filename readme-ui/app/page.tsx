import ReadmeGenerator from "@/components/ReadmeGenerator";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-blue-500/30">
      {/* Visual Header for your Empire */}
      <div className="pt-20 pb-10 text-center">
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 bg-gradient-to-b from-white to-zinc-500 bg-clip-text text-transparent">
          README ENGINE
        </h1>
        <p className="text-zinc-500 text-lg md:text-xl font-medium max-w-xl mx-auto px-6">
          High-performance metadata extraction for professional documentation. 
          Built for scale, powered by Gemini.
        </p>
      </div>

      {/* The Master Generator Component */}
      <section className="pb-20">
        <ReadmeGenerator />
      </section>

      {/* Footer Branding */}
      <footer className="py-10 border-t border-zinc-900 text-center">
        <p className="text-zinc-600 text-sm font-mono">
          &copy; 2026 Arshad | AplyEase Labs
        </p>
      </footer>
    </main>
  );
}