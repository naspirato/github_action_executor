#!/usr/bin/env python3
"""PR comment template - 3 types of comments"""
import json
import os
from generate_badges import BadgeGenerator

COLOR_BLUE = "2196f3"
COLOR_PURPLE = "9c27b0"


def _load_branches(branches_file: str = None) -> list:
    """Load branches from file, default to .github/configs/backport_branches.json"""
    if not branches_file:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        branches_file = os.path.join(repo_root, ".github/configs/backport_branches.json")
    
    with open(branches_file, 'r') as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get("branches", [])


def generate_pr_actions(gen: BadgeGenerator) -> str:
    """Generate PR actions comment with tests and backport"""
    if gen.pr_branch is None or gen.pr_number is None:
        raise ValueError("pr_branch and pr_number are required")
    
    pr, branch = str(gen.pr_number), gen.pr_branch
    branches = _load_branches()
    
    test_rows = [
        ["**All**", {"test_type": "all", "from_pr": pr}],
        ["**Unit**", {"test_type": "unit", "from_pr": pr}, COLOR_BLUE],
        ["**Integration**", {"test_type": "integration", "from_pr": pr}],
    ]
    
    backport_rows = [(f"`{b}`", {"target_branch": b, "from_pr": pr, "source_branch": branch}, COLOR_BLUE) for b in branches]
    
    test_table = gen.table("test.yml", test_rows, columns=["Test Type", "Actions"], ref=gen.base_branch)
    backport_table = gen.table("backport.yml", backport_rows, columns=["Branch", "Actions"], badge_text="Backport", ref=gen.base_branch)
    backport_custom = gen.badge("📦 Backport (Custom)", "backport.yml", ref=gen.base_branch, inputs={"from_pr": pr, "source_branch": branch}, color=COLOR_PURPLE, icon="⚙️", only_ui=True)
    
    return f"""## 🚀 Quick Actions

### 🧪 Run Tests

{test_table}

### 📦 Backport

{backport_table}

Choose branches to backport manually:

{backport_custom}

▶ - immediately runs the workflow with default parameters.

⚙️ - opens UI to review and modify parameters before running.

---
*These links will automatically comment on this PR with the workflow results.*

*Tip: To open links in a new tab, use Ctrl+Click (Windows/Linux) or Cmd+Click (macOS).*
""".strip()


def generate_simple(gen: BadgeGenerator) -> str:
    """Generate simple comment with custom badges"""
    # Add your badges here, example:
    # badge1 = gen.badge("Text", "workflow.yml", ref=gen.base_branch, inputs={}, color=COLOR_BLUE)
    badge1 = gen.badge("Example", "workflow.yml", ref=gen.base_branch, inputs={}, color=COLOR_BLUE)
    
    return f"""## 🚀 Quick Actions

{badge1}

---
""".strip()


def generate_table_only(gen: BadgeGenerator) -> str:
    """Generate comment with only a table"""
    # Add your rows here, example:
    # rows = [["Label1", {"param": "value"}], ["Label2", {"param": "value2"}, COLOR_BLUE]]
    rows = []
    
    table = gen.table("workflow.yml", rows, columns=["Label", "Actions"], ref=gen.base_branch)
    
    return f"""## 🚀 Quick Actions

{table}
""".strip()


def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser()
    parser.add_argument("comment_type", choices=["pr_actions", "simple", "table_only"], help="Comment type")
    parser.add_argument("--vars", default="vars.json", help="JSON file with vars (default: vars.json)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    # Load vars
    try:
        with open(args.vars, 'r') as f:
            vars_dict = json.load(f)
    except Exception as e:
        print(f"Error loading vars: {e}", file=sys.stderr)
        sys.exit(1)
    
    gen = BadgeGenerator(
        app_domain=vars_dict["app_domain"],
        repo_owner=vars_dict["repo_owner"],
        repo_name=vars_dict["repo_name"],
        pr_number=int(vars_dict["pr_number"]),
        pr_branch=vars_dict["pr_branch"],
        base_branch=vars_dict["base_branch"]
    )
    
    # Generate comment
    try:
        if args.comment_type == "pr_actions":
            markdown = generate_pr_actions(gen)
        elif args.comment_type == "simple":
            markdown = generate_simple(gen)
        elif args.comment_type == "table_only":
            markdown = generate_table_only(gen)
    except Exception as e:
        print(f"Error generating comment: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(markdown)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
