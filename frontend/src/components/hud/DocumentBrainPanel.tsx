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
      <label className="flex cursor-pointer items-center justify-center gap-2 border border-dashed border-primary/25 py-2 font-terminal text-[10px] uppercase text-muted-foreground hover:bg-primary/5">
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
          <div key={doc.id} className="flex items-center gap-2 border border-primary/10 px-2 py-1">
            <FileText className="h-3 w-3 text-primary/50" />
            <span className="truncate font-terminal text-[10px] text-foreground">{doc.filename}</span>
            <span className="ml-auto font-terminal text-[8px] uppercase text-muted-foreground/80">{doc.status}</span>
          </div>
        ))}
      </div>

      <div className="space-y-1 border-t border-primary/15 pt-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask your documents…"
          className="w-full border border-primary/20 bg-background/60 px-2 py-1 font-terminal text-[10px] text-foreground outline-none"
        />
        <button
          type="button"
          onClick={() => void onAsk()}
          className="w-full border border-primary/30 py-1 font-terminal text-[9px] uppercase tracking-wider text-muted-foreground hover:bg-primary/10"
        >
          Query document brain
        </button>
        {answer && (
          <p className="max-h-24 overflow-y-auto font-terminal text-[10px] leading-relaxed text-muted-foreground">
            {answer}
          </p>
        )}
      </div>
    </div>
  );
}
