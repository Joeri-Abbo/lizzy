import requests


def get_tags_of_repo(repo: str, all_tags: bool = False) -> list:
    """Fetch tags of a given GitHub repository."""
    if not all_tags:
        r = requests.get(f"https://api.github.com/repos/{repo}/tags")
        return [tag["name"] for tag in r.json()]
    else:
        tags = []
        page = 1
        while True:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/tags",
                params={"page": page, "per_page": 100},
            )
            page_tags = [tag["name"] for tag in r.json()]
            if not page_tags:
                break
            tags.extend(page_tags)
            page += 1
        return tags
