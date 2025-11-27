#!/usr/bin/env python3
import json
from pathlib import Path
import sys

badges_dir = Path(__file__).parent.parent
sys.path.insert(0, str(badges_dir))

from generate_badges import BadgeGenerator
from comment_template import generate_pr_actions, generate_simple, generate_table_only

vars_dict = json.load(open(Path(__file__).parent / "vars.json"))
gen = BadgeGenerator(**vars_dict)
output_dir = Path(__file__).parent

(output_dir / "preview_pr_actions.md").write_text(generate_pr_actions(gen))
(output_dir / "preview_simple.md").write_text(generate_simple(gen))
(output_dir / "preview_table_only.md").write_text(generate_table_only(gen))
