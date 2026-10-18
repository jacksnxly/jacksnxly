"""Fetch the numbers for the README's GitHub strip and write them as JSON.

Needs a token in GH_TOKEN. With a token that can read private repos, the merged pull request count includes them
(the contribution calendar already counts private work publicly on the profile). Never prints the token.
Usage: GH_TOKEN=... python -I fetch_stats.py <out.json> [login]
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

OUT = sys.argv[1]
LOGIN = sys.argv[2] if len(sys.argv) > 2 else "jacksnxly"
TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    sys.exit("GH_TOKEN is not set")


def call(url, data=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json", "User-Agent": "jacksnxly-readme-stats"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


today = dt.datetime.now(dt.timezone.utc).date()
since = (today - dt.timedelta(days=30)).isoformat()

cal = call("https://api.github.com/graphql", {"query": """query($login: String!) { user(login: $login) {
  contributionsCollection { contributionCalendar { totalContributions weeks { firstDay contributionDays { date contributionCount } } } } } }""",
                                              "variables": {"login": LOGIN}})["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]]
weeks = [{"first_day": w["firstDay"], "total": sum(d["contributionCount"] for d in w["contributionDays"])} for w in cal["weeks"]]

# Merged pull requests in the last 30 days, and how many repositories they went into (search returns at most 1,000 items)
q = urllib.parse.quote(f"author:{LOGIN} is:pr is:merged merged:>={since}")
first = call(f"https://api.github.com/search/issues?q={q}&per_page=100")
repos = {i["repository_url"] for i in first["items"]}
page = 2
while len(first["items"]) and (page - 1) * 100 < min(first["total_count"], 1000):
    items = call(f"https://api.github.com/search/issues?q={q}&per_page=100&page={page}")["items"]
    if not items:
        break
    repos |= {i["repository_url"] for i in items}
    page += 1

stats = {
    "updated": today.isoformat(),
    "prs_30d": first["total_count"],
    "repos_30d": len(repos),
    "contrib_30d": sum(d["contributionCount"] for d in days[-30:]),
    "contrib_year": cal["totalContributions"],
    "weeks": weeks,
}
with open(OUT, "w") as f:
    json.dump(stats, f, indent=1)
print({k: v for k, v in stats.items() if k != "weeks"}, f"{len(weeks)} weeks")
