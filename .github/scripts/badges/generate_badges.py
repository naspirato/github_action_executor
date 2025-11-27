#!/usr/bin/env python3
"""Badge generator library for GitHub Actions workflow triggers"""
from urllib.parse import urlencode, quote
from typing import Dict, List, Optional, Literal

# Default colors
DEFAULT_UI_COLOR = "ff9800"
DEFAULT_DIRECT_COLOR = "4caf50"


class BadgeGenerator:
    """Generator for GitHub Actions workflow trigger badges"""
    
    def __init__(self, app_domain: str, repo_owner: str, repo_name: str, 
                 pr_number: Optional[int] = None, pr_branch: Optional[str] = None, 
                 base_branch: Optional[str] = None):
        self.app_domain = app_domain.rstrip('/')
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.pr_branch = pr_branch
        self.base_branch = base_branch or "main"
        self.return_url = f"https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}" if pr_number else None
    
    def build_workflow_url(self, workflow_id: str, link_type: Literal["direct", "ui"] = "direct",
                          ref: Optional[str] = None, inputs: Optional[Dict[str, str]] = None,
                          return_url: Optional[str] = None, **kwargs) -> str:
        ref = ref or self.base_branch
        inputs = inputs or {}
        params = {"owner": self.repo_owner, "repo": self.repo_name, "workflow_id": workflow_id, "ref": ref}
        params.update(inputs)
        if return_url:
            params["return_url"] = return_url
        elif self.return_url:
            params["return_url"] = self.return_url
        if link_type == "ui":
            params["ui"] = "true"
        params.update(kwargs)
        return f"{self.app_domain}/workflow/trigger?{urlencode(params, doseq=True)}"
    
    def create_badge(self, text: str, workflow_id: str, link_type: Literal["direct", "ui"] = "direct",
                    ref: Optional[str] = None, inputs: Optional[Dict[str, str]] = None,
                    return_url: Optional[str] = None, badge_color: str = "2196f3",
                    badge_style: str = "flat-square", icon: Optional[str] = None, **kwargs) -> str:
        url = self.build_workflow_url(workflow_id=workflow_id, link_type=link_type, ref=ref,
                                     inputs=inputs, return_url=return_url, **kwargs)
        badge_text = f"{icon} {text}".strip() if icon else text
        badge_url = f"https://img.shields.io/badge/{quote(badge_text.replace(' ', '_'))}-{badge_color}?style={badge_style}"
        return f"[![{badge_text}]({badge_url})]({url})"
    
    def create_badge_pair(self, text: str, workflow_id: str, ref: Optional[str] = None,
                         inputs: Optional[Dict[str, str]] = None, return_url: Optional[str] = None,
                         direct_color: str = DEFAULT_DIRECT_COLOR, ui_color: str = DEFAULT_UI_COLOR,
                         badge_style: str = "flat-square", icon: Optional[str] = None, **kwargs) -> str:
        direct = self.create_badge(text, workflow_id, "direct", ref, inputs, return_url, direct_color, badge_style, icon, **kwargs)
        ui = self.create_badge("⚙️", workflow_id, "ui", ref, inputs, return_url, ui_color, badge_style, **kwargs)
        return f"{direct} {ui}"
    
    def create_table(self, rows: List[Dict], column_headers: List[str], row_formatter: callable,
                    return_url: Optional[str] = None) -> str:
        if not rows:
            return ""
        header = "| " + " | ".join(column_headers) + " |\n"
        separator = "|" + "|".join(["--------" for _ in column_headers]) + "|\n"
        table = header + separator
        for row in rows:
            cells = row_formatter(row, self)
            if len(cells) != len(column_headers):
                raise ValueError(f"Row formatter returned {len(cells)} cells, expected {len(column_headers)}")
            table += "| " + " | ".join(cells) + " |\n"
        return table
    
    def _replace_placeholders(self, v):
        """Replace placeholders in string values"""
        if isinstance(v, str):
            return v.replace("{pr_number}", str(self.pr_number)).replace("{pr_branch}", self.pr_branch or self.base_branch).replace("{base_branch}", self.base_branch)
        return v
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting from text"""
        import re
        # Remove bold **text**, *text*
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        # Remove code `text`
        text = re.sub(r'`([^`]+)`', r'\1', text)
        return text.strip()
    
    def badge(self, text: str, workflow: str, ref: str = None, inputs: dict = None, 
              color: str = DEFAULT_DIRECT_COLOR, ui_color: str = DEFAULT_UI_COLOR, icon: str = "▶", only_ui: bool = False) -> str:
        """Create badge pair or single UI badge with placeholder replacement"""
        processed = {k: self._replace_placeholders(v) for k, v in (inputs or {}).items()}
        if only_ui:
            return self.create_badge(text, workflow, link_type="ui", ref=ref or self.base_branch, 
                                   inputs=processed, return_url=self.return_url, badge_color=color, icon=icon)
        return self.create_badge_pair(text, workflow, ref=ref or self.base_branch, inputs=processed,
                                     return_url=self.return_url, direct_color=color, ui_color=ui_color, icon=icon)
    
    def table(self, workflow: str, rows: list, columns: list = None, ref: str = None, badge_text: str = None, ui_color: str = DEFAULT_UI_COLOR) -> str:
        """Create badge table with placeholder replacement"""
        table_rows = []
        for row in rows:
            label, row_inputs, color = row[0], row[1] if len(row) > 1 else {}, row[2] if len(row) > 2 else DEFAULT_DIRECT_COLOR
            processed = {k: self._replace_placeholders(v) for k, v in row_inputs.items()}
            table_rows.append({"label": label, "workflow_id": workflow, "ref": ref or self.base_branch, 
                              "inputs": processed, "badge_color": color, "ui_color": ui_color, "icon": "▶", "return_url": self.return_url, 
                              "badge_text": badge_text or self._strip_markdown(label)})
        def formatter(row, g):
            return [row["label"], g.create_badge_pair(row["badge_text"], row["workflow_id"], ref=row["ref"], 
                    inputs=row["inputs"], return_url=row["return_url"], direct_color=row["badge_color"], ui_color=row.get("ui_color", DEFAULT_UI_COLOR), icon=row["icon"])]
        return self.create_table(rows=table_rows, column_headers=columns or ["Label", "Actions"], row_formatter=formatter)
