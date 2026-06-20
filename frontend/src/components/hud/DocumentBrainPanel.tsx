"use client";

import { useCallback, useEffect, useState } from "react";
import { FileText, Upload } from "lucide-react";
import {
  askDocument,
  listDocuments,
  uploadDocument,
  type DocumentRecord,
} from "@/lib/api";

export function DocumentBrainPanel() {
  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const refresh = useCallback(async () => {
    setDocs(await listDocuments().catch(() => []));
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function onUpload(file: File) {
    setUploading(true);
    try {
      await uploadDocument(file);
      await refresh();
    } finally {
      setUploading(false);
    }
  }

  async function onAsk() {
    if (!query.trim()) return;
    const res = await askDocument(query.trim());
    setAnswer(res.answer);
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <label className="flex cursor-pointer items-center justify-center gap-2 border border-dashed border-amber-400/25 py-2 font-terminal text-[10px] uppercase text-amber-300/55 hover:bg-amber-500/5">
        <Upload className="h-3 w-3" />
        {uploading ? "Processing…" : "Upload document"}
        <input
          type="file"
          className="hidden"
          accept=".pdf,.docx,.txt,.md,.markdown"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void onUpload(f);
            e.target.value = "";
          }}
        />
      </label>

      <div className="min-h-0 flex-1 space-y-1 overflow-y-auto">
        {docs.map((doc) => (
          <div key={doc.id} className="flex items-center gap-2 border border-amber-400/10 px-2 py-1">
            <FileText className="h-3 w-3 text-amber-400/50" />
            <span className="truncate font-terminal text-[10px] text-amber-100">{doc.filename}</span>
            <span className="ml-auto font-terminal text-[8px] uppercase text-amber-300/40">{doc.status}</span>
          </div>
        ))}
      </div>

      <div className="space-y-1 border-t border-amber-400/15 pt-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask your documents…"
          className="w-full border border-amber-400/20 bg-black/30 px-2 py-1 font-terminal text-[10px] text-amber-100 outline-none"
        />
        <button
          type="button"
          onClick={() => void onAsk()}
          className="w-full border border-amber-400/30 py-1 font-terminal text-[9px] uppercase tracking-wider text-amber-200/70 hover:bg-amber-500/10"
        >
          Query document brain
        </button>
        {answer && (
          <p className="max-h-24 overflow-y-auto font-terminal text-[10px] leading-relaxed text-amber-200/65">
            {answer}
          </p>
        )}
      </div>
    </div>
  );
}
