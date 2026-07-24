import os
import requests
from datetime import datetime
from dateutil import relativedelta

# --- Configuration ---
try:
    import config
    ACCESS_TOKEN = config.ACCESS_TOKEN
    USER_NAME = config.USER_NAME
except ImportError:
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    USER_NAME = os.environ.get('USER_NAME', 'TranHoangXuanNguyen')

HEADERS = {'Authorization': f'token {ACCESS_TOKEN}'}
GRAPHQL_URL = 'https://api.github.com/graphql'

BIRTHDAY = datetime(2005, 6, 21)  # YYYY, MM, DD=


def run_query(query, variables=None):
    """Make POST request to GitHub GraphQL API."""
    response = requests.post(
        GRAPHQL_URL,
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL Error: {result['errors']}")
        return result['data']
    else:
        raise Exception(f"Query failed ({response.status_code}): {response.text}")


def get_user_stats(username):
    """Fetch repos, stars, followers, commits."""
    query = """
    query($username: String!) {
      user(login: $username) {
        followers {
          totalCount
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazers {
              totalCount
            }
          }
        }
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    data = run_query(query, {'username': username})['user']

    followers = data['followers']['totalCount']
    repos_count = data['repositories']['totalCount']
    contributed = data['repositoriesContributedTo']['totalCount']
    stars_count = sum(repo['stargazers']['totalCount'] for repo in data['repositories']['nodes'])
    commits_count = (
        data['contributionsCollection']['totalCommitContributions'] +
        data['contributionsCollection']['restrictedContributionsCount']
    )

    return {
        'followers': followers,
        'repos': repos_count,
        'contributed': contributed,
        'stars': stars_count,
        'commits': commits_count,
    }


def get_lines_of_code(username):
    """Calculate total LOC added/deleted across owned repos."""
    headers = {
        'Authorization': f'token {ACCESS_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    repos_resp = requests.get(
        f'https://api.github.com/users/{username}/repos?per_page=100&type=owner',
        headers=headers
    )
    loc_add = 0
    loc_del = 0

    if repos_resp.status_code == 200:
        repos = repos_resp.json()
        for repo in repos:
            if repo.get('fork'):
                continue
            repo_name = repo['name']
            stats_resp = requests.get(
                f'https://api.github.com/repos/{username}/{repo_name}/stats/contributors',
                headers=headers
            )
            if stats_resp.status_code == 200 and stats_resp.json():
                for contributor in stats_resp.json():
                    if contributor.get('author', {}).get('login') == username:
                        for week in contributor.get('weeks', []):
                            loc_add += week.get('a', 0)
                            loc_del += week.get('d', 0)

    total = loc_add - loc_del
    return loc_add, loc_del, total if total > 0 else loc_add


def calculate_uptime():
    """Calculate age from birthday."""
    now = datetime.now()
    diff = relativedelta.relativedelta(now, BIRTHDAY)
    return f"{diff.years} years, {diff.months} months, {diff.days} days"


def format_number(n):
    """Format number with commas: 1234 -> 1,234"""
    return f"{n:,}"


# ============================================================
# ASCII ART - Thay đổi ASCII art của bạn ở đây
# ============================================================
ASCII_ART = [
    r"   --------------------------------------------",
    r"   -------------     ----::::--  --------------",
    r"   ----------- :!|uvuzzzc****cov!:-------------",
    r"   ----------~uc0QQ0000QQQQ000000*z~-----------",
    r"   ---------IOQ0000OOO000OOO0Q00000*|----------",
    r"   --------u0000**OO*zu|I!+!IuzcO0000z:--------",
    r"   --------vQ00Oc**zI~~~_____~+!|o000O~--------",
    r"   --------~*00cv*vI!+~~~~~+++!I!Ic00c---------",
    r"   ---------_*OIIuuuuI!+~~+!IuIII+IOOI---------",
    r"   ---------_zz++++!!++!~~~~+!+++++zu~---------",
    r"   ---------:||+++~__+!!++++~___~++I!:---------",
    r"   ----------_+!!++~~!!!++++~~~~+++_:----------",
    r"   ------------_!!+++!IIII!!++~+++_------------",
    r"   ----------:::_+!!+++++++++++++_-------------",
    r"   ---------:::::+I!!!+++++++!!!+_:------------",
    r"   ------:::::::!|!!!!!!+++++++++u|------------",
    r"   ::::::::::::::!!+~++++~~~~~~~+|_--:---------",
    r"   :::---::::::::~++++~~~~~~~~~+!+:------------",
    r"   -----:::::::::::__~~~~~~~~~_::_+_:--::------",
    r"   ------:---::-----:-:_~~~_:-::----:--:-------",
    r"   ------::-------------:~:--------------------",
    r"   -:::--:::-----------::---------------------:",
    r"   -:::::::---------::::----------------:::--::",
    r"   :::::::::-------:::::----:------------::::::",
]

# ============================================================
# INFO TEMPLATE - Thay đổi thông tin của bạn ở đây
# ============================================================
def build_info_lines(stats, loc_add, loc_del, loc_total):
    """Build the right-side info lines with live data."""
    uptime = calculate_uptime()
    return [
        f"nguyen@profile ——————————————————————————————————————",
        f". OS:                    Ubuntu 24.04, Arch Linux",
        f". Uptime:                {uptime}",
        f". Host:                  Vietnam",
        f". Kernel:                Backend Developer / DevOps Learner",
        f". IDE:                   VSCode, IntelliJ IDEA",
        f".",
        f". Languages.Programming: TypeScript, JavaScript, Python, Bash",
        f". Languages.Computer:    HTML, CSS, JSON, YAML",
        f". Languages.Real:        Vietnamese, English",
        f".",
        f". Stack.Backend:         NestJS, Express, PostgreSQL, Redis",
        f". Stack.DevOps:          Docker, K8s, GitHub Actions, Grafana",
        f".",
        f"— Contact ———————————————————————————————————————————",
        f". Email.Personal:        hoangnguyendepgiai@gmail.com",
        f". Facebook:              https://web.facebook.com/xuannguyen2106",
        f". LinkedIn:              https://www.linkedin.com/in/tranhoangxuannguyen/",
        f". Portfolio:             https://tranhoangxuannguyen.github.io/react-vite-portfolio/",
        f".",
        f"— GitHub Stats ——————————————————————————————————————",
        f". Repos:  {format_number(stats['repos'])} {{Contributed: {format_number(stats['contributed'])}}} | Stars:  {format_number(stats['stars'])}",
        f". Commits:          {format_number(stats['commits'])} | Followers:      {format_number(stats['followers'])}",
        f". Lines of Code:    {format_number(loc_total)} ( {format_number(loc_add)}++, {format_number(loc_del)}-- )",
    ]


def build_readme(ascii_lines, info_lines, ascii_width=46):
    """Combine ASCII art (left) + info (right) into a single block."""
    max_lines = max(len(ascii_lines), len(info_lines))
    combined = []
    for i in range(max_lines):
        left = ascii_lines[i] if i < len(ascii_lines) else ""
        right = info_lines[i] if i < len(info_lines) else ""
        combined.append(f"{left.ljust(ascii_width)} {right}")
    return combined


def main():
    print("Fetching GitHub stats...")
    stats = get_user_stats(USER_NAME)
    print(f"Stats: {stats}")

    print("Calculating Lines of Code...")
    loc_add, loc_del, loc_total = get_lines_of_code(USER_NAME)
    print(f"LOC: +{loc_add} / -{loc_del} = {loc_total}")

    info_lines = build_info_lines(stats, loc_add, loc_del, loc_total)
    combined = build_readme(ASCII_ART, info_lines)

    # Write README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("```\n")
        for line in combined:
            f.write(line + "\n")
        f.write("```\n")

    print("README.md updated successfully!")


if __name__ == '__main__':
    main()
