# Badge Generator Scripts

Simple Python scripts for generating GitHub Actions workflow trigger badges in PR comments.

## 📁 File Structure

```
.github/
├── scripts/badges/
│   ├── generate_badges.py      # Library - badge generation functions
│   ├── comment_template.py     # Template script with subcommands
│   ├── vars.json               # Test variables (example)
│   └── README.md               # This file
└── configs/
    └── branches.json           # Branches list for backport
```

## 🎯 Quick Start

### Basic Usage

```bash
# Generate PR actions comment (tests + backport)
python3 .github/scripts/badges/comment_template.py \
  --vars vars.json \
  pr_actions \
  --branches-file branches.json \
  --output comment.txt
```

### Comment Types

#### 1. `pr_actions` - Full PR comment with tests and backport

```bash
python3 comment_template.py --vars vars.json pr_actions \
  --branches-file branches.json \
  [--test-rows '[...]']
```

**Required:**
- `--branches-file` - JSON file with branches list

**Optional:**
- `--test-rows` - JSON array with test rows: `[["Label", {"input": "value"}, "color"], ...]`

#### 2. `simple` - Simple comment with custom badges

```bash
python3 comment_template.py --vars vars.json simple \
  --badge "🧪 Tests" "Run Tests" "test.yml" \
  --badge-color "4caf50" \
  --badge "🔨 Build" "Build" "build.yml" \
  --badge-color "2196f3" \
  [--header "Custom Header"] \
  [--footer "Custom Footer"]
```

**Required:**
- `--badge TITLE TEXT WORKFLOW` - At least one badge (can be repeated)

**Optional per badge:**
- `--badge-color COLOR` - Color for last badge
- `--badge-icon ICON` - Icon for last badge
- `--badge-ref REF` - Branch for last badge
- `--badge-inputs JSON` - JSON inputs for last badge
- `--badge-only-ui` - Only UI badge for last badge

#### 3. `table_only` - Comment with only a table

```bash
python3 comment_template.py --vars vars.json table_only \
  --workflow "test.yml" \
  --rows '[["All", {"test_type": "all"}, "4caf50"], ["Unit", {"test_type": "unit"}, "2196f3"]]' \
  --columns '["Test", "Actions"]' \
  [--ref "main"] \
  [--badge-text "Run"] \
  [--header "Custom Header"]
```

**Required:**
- `--workflow` - Workflow file name
- `--rows` - JSON array: `[["Label", {"input": "value"}, "color"], ...]`

**Optional:**
- `--columns` - JSON array with column headers (default: `["Label", "Actions"]`)
- `--ref` - Branch name (default: `main`)
- `--badge-text` - Badge text (default: label)
- `--header` - Comment header (default: `## 🚀 Quick Actions`)

## 📚 Architecture

### Library (`generate_badges.py`)

Core badge generation functions:

- `BadgeGenerator` class - Main generator
- `create_badge()` - Single badge (direct or UI)
- `create_badge_pair()` - Pair of badges (direct + UI)
- `create_table()` - Markdown table with badges
- `badge()` - Helper with placeholder replacement
- `table()` - Helper with placeholder replacement

### Template (`comment_template.py`)

Script with subcommands for different comment types:

- `pr_actions` - Full PR comment
- `simple` - Custom badges
- `table_only` - Table only

Edit `comment_template.py` to customize templates!

## 🔧 Variables File Format

`vars.json`:
```json
{
  "app_domain": "https://your-app.com",
  "repo_owner": "owner",
  "repo_name": "repo",
  "pr_number": 123,
  "pr_branch": "feature-branch",
  "base_branch": "main"
}
```

## 🚀 Integration

### Use in GitHub Actions

```yaml
- name: Generate badge comment
  run: |
    cat > vars.json << EOF
    {
      "app_domain": "${{ vars.APP_DOMAIN }}",
      "repo_owner": "${{ github.repository_owner }}",
      "repo_name": "${{ github.event.repository.name }}",
      "pr_number": ${{ github.event.pull_request.number }},
      "pr_branch": "${{ github.event.pull_request.head.ref }}",
      "base_branch": "${{ github.event.pull_request.base.ref }}"
    }
    EOF
    
    python3 .github/scripts/badges/comment_template.py \
      --vars vars.json \
      pr_actions \
      --branches-file .github/configs/branches.json \
      --output comment.txt
```

## 📝 API Reference

### BadgeGenerator

```python
from generate_badges import BadgeGenerator

gen = BadgeGenerator(
    app_domain="https://your-app.com",
    repo_owner="owner",
    repo_name="repo",
    pr_number=123,
    pr_branch="feature",
    base_branch="main"
)

# Create badge pair
badge = gen.badge("Run Tests", "test.yml", 
                  inputs={"test_type": "all"}, 
                  color="4caf50")

# Create table
table = gen.table("test.yml", 
                  rows=[("All", {"test_type": "all"}, "4caf50")],
                  columns=["Test", "Actions"])
```

## 📄 License

This script is part of the GitHub Action Executor project.
