#!/usr/bin/env python3
"""
Reflection Agent — Deterministic End-of-Day Reflection Tool
No LLM calls at runtime. Pure tree traversal with state accumulation.
"""

import json
import os
import sys
import time
from pathlib import Path


# ─── Terminal helpers ─────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_slow(text: str, delay: float = 0.018):
    """Print text character by character for a calm, deliberate feel."""
    for ch in text:
        print(ch, end="", flush=True)
        if ch not in (" ", "\n"):
            time.sleep(delay)
    print()

def divider():
    print("\n" + "─" * 58 + "\n")

def print_box(text: str):
    lines = text.strip().split("\n")
    width = max(len(l) for l in lines) + 4
    print("┌" + "─" * width + "┐")
    for line in lines:
        print("│  " + line.ljust(width - 2) + "  │")
    print("└" + "─" * width + "┘")


# ─── State ────────────────────────────────────────────────────────────────────

class State:
    def __init__(self):
        self.answers: dict[str, str] = {}   # node_id → chosen option text
        self.signals: dict[str, dict[str, int]] = {
            "axis1": {"internal": 0, "external": 0},
            "axis2": {"contribution": 0, "entitlement": 0, "neutral": 0},
            "axis3": {"self": 0, "team": 0, "other": 0, "transcendent": 0},
        }

    def record_signal(self, signal: str):
        if ":" in signal:
            axis, pole = signal.split(":", 1)
            if axis in self.signals and pole in self.signals[axis]:
                self.signals[axis][pole] += 1

    def dominant(self, axis: str) -> str:
        counts = self.signals.get(axis, {})
        if not counts or all(v == 0 for v in counts.values()):
            return list(counts.keys())[0]
        return max(counts, key=lambda k: counts[k])

    def interpolate(self, text: str) -> str:
        """Replace {NODE_ID} placeholders with recorded answers."""
        for node_id, answer in self.answers.items():
            text = text.replace("{" + node_id + "}", answer)
        return text


# ─── Tree loader ──────────────────────────────────────────────────────────────

def load_tree(path: str) -> dict[str, dict]:
    with open(path) as f:
        nodes_list = json.load(f)
    return {node["id"]: node for node in nodes_list}


# ─── Node handlers ────────────────────────────────────────────────────────────

def handle_start(node: dict, state: State) -> str:
    clear()
    divider()
    print_slow(state.interpolate(node["text"]))
    divider()
    input("  Press Enter to begin... ")
    return _first_child(node, state)


def handle_question(node: dict, state: State, tree: dict) -> str:
    clear()
    divider()
    print_slow("  " + state.interpolate(node["text"]))
    print()

    options = node["options"]
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    print()

    while True:
        raw = input("  Your choice (number): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            chosen = options[int(raw) - 1]
            break
        print("  Please enter a number between 1 and", len(options))

    state.answers[node["id"]] = chosen

    # Record signal if present
    signals_map = node.get("signals", {})
    if chosen in signals_map:
        state.record_signal(signals_map[chosen])

    divider()
    return _first_child(node, state)


def handle_decision(node: dict, state: State) -> str:
    """Invisible routing — no user interaction."""
    # Pattern 1: direct answer→node mapping
    if "rules" in node:
        # Get the answer to the parent question
        parent_id = node.get("parentId")
        if parent_id and parent_id in state.answers:
            answer = state.answers[parent_id]
            if answer in node["rules"]:
                return node["rules"][answer]

    # Pattern 2: signal-dominant routing
    if "rules_signal" in node:
        for axis, pole_map in node["rules_signal"].items():
            dom = state.dominant(axis)
            if dom in pole_map:
                return pole_map[dom]

    # Fallback: first value in rules
    if "rules" in node:
        return list(node["rules"].values())[0]
    if "rules_signal" in node:
        for axis, pole_map in node["rules_signal"].items():
            return list(pole_map.values())[0]

    return _first_child(node, state)


def handle_reflection(node: dict, state: State) -> str:
    clear()
    divider()
    print("  ✦ REFLECTION\n")
    print_slow(state.interpolate(node["text"]))
    divider()
    input("  Take a moment. Press Enter when ready... ")
    return _first_child(node, state)


def handle_bridge(node: dict, state: State) -> str:
    clear()
    divider()
    print_slow("  " + state.interpolate(node["text"]))
    divider()
    time.sleep(1.2)
    return node.get("target") or _first_child(node, state)


def handle_summary(node: dict, state: State) -> str:
    clear()
    divider()
    print("  ✦ TODAY'S REFLECTION SUMMARY\n")

    # Build the interpolated summary text
    summaries = node.get("summaries", {})

    axis1_dom = state.dominant("axis1")
    axis2_dom = state.dominant("axis2")
    axis3_dom = state.dominant("axis3")

    axis1_info = summaries.get("axis1", {}).get(axis1_dom, {})
    axis2_info = summaries.get("axis2", {}).get(axis2_dom, {})
    axis3_info = summaries.get("axis3", {}).get(axis3_dom, {})

    text = node["text"]
    text = text.replace("{axis1_label}", axis1_info.get("label", axis1_dom))
    text = text.replace("{axis1_summary}", axis1_info.get("text", ""))
    text = text.replace("{axis2_label}", axis2_info.get("label", axis2_dom))
    text = text.replace("{axis2_summary}", axis2_info.get("text", ""))
    text = text.replace("{axis3_label}", axis3_info.get("label", axis3_dom))
    text = text.replace("{axis3_summary}", axis3_info.get("text", ""))

    text = state.interpolate(text)
    print_box(text)
    divider()
    input("  Press Enter to close... ")
    return _first_child(node, state)


def handle_end(node: dict, state: State):
    clear()
    divider()
    print_slow("  " + node["text"])
    divider()
    print()


# ─── Tree traversal ───────────────────────────────────────────────────────────

def _first_child(node: dict, state: State) -> str | None:
    """Find the first node in tree whose parentId matches this node's id."""
    return None  # resolved at walk time via adjacency


def walk(tree: dict, state: State):
    # Build parent→children map
    children: dict[str, list[str]] = {}
    for nid, node in tree.items():
        pid = node.get("parentId")
        if pid:
            children.setdefault(pid, []).append(nid)

    def next_node(current_id: str, explicit_next: str | None = None) -> str | None:
        if explicit_next:
            return explicit_next
        kids = children.get(current_id, [])
        return kids[0] if kids else None

    current_id = "START"

    while current_id and current_id in tree:
        node = tree[current_id]
        ntype = node.get("type")

        if ntype == "start":
            nxt = next_node(current_id)
            handle_start(node, state)
            current_id = nxt

        elif ntype == "question":
            handle_question(node, state, tree)
            # After a question, check if next child is a decision
            kids = children.get(current_id, [])
            current_id = kids[0] if kids else None

        elif ntype == "decision":
            target = handle_decision(node, state)
            current_id = target

        elif ntype == "reflection":
            handle_reflection(node, state)
            kids = children.get(current_id, [])
            # After reflection, jump to BRIDGE if the next sibling path leads there
            # We check if there's a bridge targeting our next axis
            current_id = kids[0] if kids else _find_bridge(current_id, tree, children)

        elif ntype == "bridge":
            target = handle_bridge(node, state)
            current_id = target

        elif ntype == "summary":
            handle_summary(node, state)
            kids = children.get(current_id, [])
            current_id = kids[0] if kids else None

        elif ntype == "end":
            handle_end(node, state)
            current_id = None

        else:
            current_id = next_node(current_id)


def _find_bridge(from_id: str, tree: dict, children: dict) -> str | None:
    """Find the next bridge node that has no parentId (orphan bridge, transition marker)."""
    # Bridges with no parentId are axis transitions — find next one
    bridges = [nid for nid, n in tree.items() if n.get("type") == "bridge"]
    for b in bridges:
        if tree[b].get("target"):
            return b
    return None


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    tree_path = Path(__file__).parent.parent / "tree" / "reflection-tree.json"
    if len(sys.argv) > 1:
        tree_path = Path(sys.argv[1])

    if not tree_path.exists():
        print(f"Error: tree file not found at {tree_path}")
        sys.exit(1)

    tree = load_tree(str(tree_path))
    state = State()

    try:
        walk(tree, state)
    except KeyboardInterrupt:
        print("\n\n  Session ended early. See you tomorrow.\n")


if __name__ == "__main__":
    main()