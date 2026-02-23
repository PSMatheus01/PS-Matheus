import os
import re
import requests

GITHUB_USERNAME = "psmatheus01"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
STATS_BASE = "https://github-readme-stats-eight-eta-69.vercel.app"
LIMIT = 6


def get_recent_repos(limit: int) -> list[dict]:
    """Fetch the most recently updated public repos, excluding the profile repo."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    url = (
        f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        f"?sort=updated&direction=desc&per_page=20&type=public"
    )
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    repos = [
        r for r in response.json()
        if not r["fork"] and r["name"] != GITHUB_USERNAME
    ]
    return repos[:limit]


def build_projects_section(repos: list[dict]) -> str:
    """Build the markdown block for the Featured Projects section."""
    lines = []

    # Two cards per row
    for i in range(0, len(repos), 2):
        pair = repos[i : i + 2]
        row_parts = []
        for repo in pair:
            card_url = (
                f"{STATS_BASE}/api/pin/"
                f"?username={GITHUB_USERNAME}"
                f"&repo={repo['name']}"
                f"&bg_color=0d0d0d"
                f"&title_color=00ff38"
                f"&text_color=f0f0f0"
                f"&icon_color=6000ff"
                f"&border_color=6000ff"
                f"&hide_border=false"
            )
            link_url = repo["html_url"]
            row_parts.append(
                f'<a href="{link_url}">'
                f'<img src="{card_url}" width="48%" alt="{repo["name"]}"/>'
                f"</a>"
            )
        lines.append(
            '<div align="center">\n'
            + "&nbsp;&nbsp;".join(row_parts)
            + "\n</div>\n<br/>"
        )

    # View all button
    lines.append(
        '\n<div align="center">\n'
        f'<a href="https://github.com/{GITHUB_USERNAME}?tab=repositories">\n'
        f'<img src="https://img.shields.io/badge/View_all_repositories-6000ff?style=for--the--badge&logoColor=white" alt="View all repositories"/>\n'
        f"</a>\n</div>"
    )

    return "\n".join(lines)


def update_readme(new_section: str) -> None:
    """Replace the content between the PROJECTS markers in README.md."""
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"(<!-- PROJECTS:START -->).*?(<!-- PROJECTS:END -->)",
        re.DOTALL,
    )

    if not pattern.search(content):
        print("ERROR: PROJECTS markers not found in README.md")
        return

    updated = pattern.sub(
        rf"\1\n{new_section}\n\2",
        content,
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"Updated with {LIMIT} repositories.")


if __name__ == "__main__":
    repos = get_recent_repos(LIMIT)
    section = build_projects_section(repos)
    update_readme(section)
