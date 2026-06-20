/**
 * Ketu Memory Constellation — expandable hooks for future memory graph UI.
 * Not fully built; architecture only.
 */

export type MemoryNodeKind = "project" | "document" | "conversation" | "knowledge" | "goal";

export interface MemoryConstellationNode {
  id: string;
  kind: MemoryNodeKind;
  label: string;
  /** Future: pgvector embedding id */
  embeddingRef?: string;
  /** Future: link to Ketu graha orbit anchor */
  ketuAnchor?: { angle: number; distance: number };
}

export type MemoryNodeListener = (nodes: MemoryConstellationNode[]) => void;

const listeners = new Set<MemoryNodeListener>();
let nodes: MemoryConstellationNode[] = [];

/** Register a memory node for future Ketu constellation visualization */
export function registerMemoryNode(node: MemoryConstellationNode): void {
  nodes = [...nodes.filter((n) => n.id !== node.id), node];
  listeners.forEach((fn) => fn(nodes));
}

export function unregisterMemoryNode(id: string): void {
  nodes = nodes.filter((n) => n.id !== id);
  listeners.forEach((fn) => fn(nodes));
}

export function getMemoryNodes(): readonly MemoryConstellationNode[] {
  return nodes;
}

export function subscribeMemoryConstellation(fn: MemoryNodeListener): () => void {
  listeners.add(fn);
  fn(nodes);
  return () => listeners.delete(fn);
}

/** Ketu graha id — memory librarian force */
export const KETU_GRAHA_ID = "ketu" as const;

export const MEMORY_NODE_KINDS: MemoryNodeKind[] = [
  "project",
  "document",
  "conversation",
  "knowledge",
  "goal",
];
