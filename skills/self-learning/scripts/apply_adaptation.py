#!/usr/bin/env python3
"""
Apply an adaptation to agent behavior.

Usage: python scripts/apply_adaptation.py --agent worker --adaptation "Always run lsp_diagnostics"

Supports levels: session, agent, system
"""

import argparse
from pathlib import Path
from datetime import datetime


def apply_session_adaptation(agent, adaptation):
    """Apply session-local adaptation."""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    adaptation_file = Path(f".tmp/learning/adaptations/session_{session_id}.md")

    with open(adaptation_file, "w") as f:
        f.write(f"# Session Adaptation: {agent}\n")
        f.write(f"Applied: {datetime.now()}\n\n")
        f.write(f"**Adaptation**: {adaptation}\n")
        f.write(f"**Level**: Session-local\n")
        f.write(f"**Impact**: Applied to current session only\n")

    print(f"Session adaptation saved to {adaptation_file}")


def apply_agent_adaptation(agent, adaptation, agent_file):
    """Apply agent-specific adaptation."""
    agent_path = Path(agent_file)

    with open(agent_path, "r") as f:
        content = f.read()

    # Find "## Workflow" or similar section
    if "## Workflow" in content:
        insertion_point = content.find("## Workflow")
        adapted_content = (
            content[:insertion_point]
            + f"## Learning Rule (Self-Improving)\n{adaptation}\n\n"
            + content[insertion_point:]
        )
    else:
        adapted_content = (
            content + f"\n\n## Learning Rule (Self-Improving)\n{adaptation}\n"
        )

    with open(agent_path, "w") as f:
        f.write(adapted_content)

    print(f"Agent adaptation applied to {agent_path}")


def apply_system_adaptation(adaptation):
    """Apply system-wide adaptation (requires approval)."""
    print(f"SYSTEM-WIDE ADAPTATION REQUESTED:")
    print(f"  Adaptation: {adaptation}")
    print(f"\nThis requires manual approval.")
    print("Document in .tmp/learning/adaptations/system_pending.md")
    print("Then update relevant agent files after review.")

    pending_file = Path(".tmp/learning/adaptations/system_pending.md")
    pending_file.parent.mkdir(parents=True, exist_ok=True)

    with open(pending_file, "a") as f:
        f.write(f"# System-Wide Adaptation (Pending Approval)\n")
        f.write(f"Requested: {datetime.now()}\n")
        f.write(f"**Adaptation**: {adaptation}\n")
        f.write(f"**Status**: Pending manual review\n\n")

    print(f"Adaptation documented in {pending_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agent", required=True, help="Agent name (e.g., worker, orchestrator)"
    )
    parser.add_argument("--adaptation", required=True, help="Adaptation description")
    parser.add_argument(
        "--level",
        default="session",
        choices=["session", "agent", "system"],
        help="Adaptation level",
    )
    parser.add_argument(
        "--agent-file", help="Path to agent .md file (required for agent level)"
    )
    args = parser.parse_args()

    if args.level == "session":
        apply_session_adaptation(args.agent, args.adaptation)
    elif args.level == "agent":
        if not args.agent_file:
            raise ValueError("--agent-file required for agent-level adaptations")
        apply_agent_adaptation(args.agent, args.adaptation, args.agent_file)
    elif args.level == "system":
        apply_system_adaptation(args.adaptation)


if __name__ == "__main__":
    main()
