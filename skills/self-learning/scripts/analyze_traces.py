#!/usr/bin/env python3
"""
Analyze collected traces to extract patterns and insights.

Usage: python scripts/analyze_traces.py --traces .tmp/learning/traces/

Output: .tmp/learning/insights/
"""

import argparse
import re
from pathlib import Path
from collections import Counter


def load_trace(trace_path):
    """Load and parse a trace file."""
    with open(trace_path) as f:
        content = f.read()
    # Extract structured data from trace
    return {
        "agent": extract_field(content, "Agent"),
        "status": extract_field(content, "Status"),
        "tools": extract_tools(content),
        "failures": extract_failures(content),
    }


def extract_field(content, field):
    """Extract a field from trace content."""
    pattern = f"{field}:\\s*(.+?)(?:\\n|$)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def extract_tools(content):
    """Extract tools used from trace."""
    tools = re.findall(r"- ([\w_]+):", content)
    return Counter(tools)


def extract_failures(content):
    """Extract failure patterns from trace."""
    failures = re.findall(r"(?:Error|Failure):\s*(.+)", content)
    return failures


def identify_patterns(traces):
    """Identify patterns across traces."""
    # Success patterns
    success_traces = [t for t in traces if t["status"] == "Success"]
    success_tools = Counter()
    for t in success_traces:
        success_tools.update(t["tools"])

    # Failure patterns
    failure_traces = [t for t in traces if t["status"] == "Failure"]
    failure_patterns = Counter()
    for t in failure_traces:
        failure_patterns.update(t["failures"])

    return {
        "success_tools": success_tools,
        "failure_patterns": failure_patterns,
        "success_rate": len(success_traces) / len(traces) if traces else 0,
    }


def generate_insights(patterns):
    """Generate actionable insights from patterns."""
    insights = []

    # Success pattern: Tools consistently used in successful traces
    for tool, count in patterns["success_tools"].most_common(5):
        insight = {
            "category": "Success Patterns",
            "finding": f"Tool '{tool}' appears in {count} successful traces",
            "action": f"Consider making '{tool}' mandatory for relevant tasks",
            "impact": "High" if count > 5 else "Medium",
        }
        insights.append(insight)

    # Failure pattern: Recurring issues
    for pattern, count in patterns["failure_patterns"].most_common(5):
        insight = {
            "category": "Failure Patterns",
            "finding": f"Failure pattern '{pattern}' occurs {count} times",
            "action": f"Add validation to prevent: {pattern}",
            "impact": "High" if count > 3 else "Medium",
        }
        insights.append(insight)

    return insights


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", required=True, help="Path to traces directory")
    parser.add_argument(
        "--output", default=".tmp/learning/adaptations", help="Output directory"
    )
    args = parser.parse_args()

    # Load all traces
    trace_dir = Path(args.traces)
    traces = [load_trace(f) for f in trace_dir.glob("*.md")]

    # Identify patterns
    patterns = identify_patterns(traces)

    # Generate insights
    insights = generate_insights(patterns)

    # Save insights
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    for insight in insights:
        category = insight["category"].replace(" ", "_").lower()
        output_file = output_dir / f"{category}.md"

        with open(output_file, "a") as f:
            f.write(f"## Insight: {insight['finding']}\n")
            f.write(f"**Category**: {insight['category']}\n")
            f.write(f"**Action**: {insight['action']}\n")
            f.write(f"**Impact**: {insight['impact']}\n\n")

    print(f"Generated {len(insights)} insights in {output_dir}")


if __name__ == "__main__":
    main()
