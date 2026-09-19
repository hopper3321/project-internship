export function AboutPage() {
  return (
    <div className="prose prose-slate max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">About EcoSort AI</h1>
      <p>
        EcoSort AI is a B.Tech CSE AI project that helps users identify waste, understand
        recyclability, and learn correct disposal—supporting{" "}
        <strong>UN SDG 12: Responsible Consumption and Production</strong>.
      </p>
      <section>
        <h2 className="text-xl font-semibold">Responsible AI</h2>
        <ul className="list-disc pl-5 space-y-2 text-slate-700">
          <li>AI-generated guidance is informational; verify local municipal rules.</li>
          <li>Sources from RAG are shown by document name—no fabricated citations.</li>
          <li>No unnecessary personal data is collected; history stays in your browser.</li>
          <li>Hazardous waste information avoids dangerous handling instructions.</li>
          <li>Demo mode is clearly labeled when IBM Granite is not connected.</li>
        </ul>
      </section>
      <section>
        <h2 className="text-xl font-semibold">Architecture highlights</h2>
        <ul className="list-disc pl-5 space-y-1 text-slate-700">
          <li>React + Flask REST API</li>
          <li>IBM Granite via watsonx.ai (when configured)</li>
          <li>ChromaDB RAG pipeline with PDF/TXT/DOCX ingestion</li>
          <li>Agent routing for waste analysis, document search, and summarization</li>
          <li>Entity extraction on each text analysis</li>
        </ul>
      </section>
    </div>
  );
}
