"""Module for generating the CHANGELOG.md"""

from collections import defaultdict
from nboost import __version__
from datetime import datetime
from pathlib import Path
import git

REPO = git.Repo()
COMMIT_URL = 'https://github.com/koursaros-ai/nboost/commit/%s'

FMT = (
    ' - [[```{sha}```]({url})] {msg} (*{name}*) '
    '<span style="color:blue">△{changes}</span>'
)

EMOJIS = {
    'proxy': '📡',
    'base': '🏠',
    'benchmark': '📏',
    'codex': '📖',
    'helpers': '🧰',
    'protocol': '🌐',
    'server': '🖥️',
    'stats': '⏱',
    'tutorial': '🆕',
    'cli': '⌨️',
    'model': '🧠'
}


def get_last_release() -> datetime:
    """get the last commit date of __version__"""
    for commit in REPO.iter_commits(paths=__version__.__file__):
        return commit.committed_date


LAST_RELEASE = get_last_release()


def get_changelog() -> dict:
    """construct changelog dict"""
    changelog = defaultdict(list)
    for commit in REPO.iter_commits():
        for file in commit.stats.files:
            if file.startswith('nboost') and not commit.summary.startswith('Merge'):
                line = FMT.format(
                    sha=commit.hexsha[:7],
                    url=COMMIT_URL % commit.hexsha,
                    msg=commit.summary.split(': ')[-1],
                    name=commit.committer.name,
                    changes=commit.stats.total['lines']
                )
                module = file.split('/')[1].split('.')[0]
                changelog[module].append(line)
        if commit.committed_date < LAST_RELEASE:
            break
    return changelog


def format_changelog(changelog: dict) -> str:
    """create .md from changelog dict"""
    release = '# Release `%s`' % __version__.__doc__

    for module, lines in changelog.items():
        release += '\n\n### %s %s\n' % (EMOJIS.get(module, ''), module.title())
        for line in lines:
            release += '\n' + line
    return release


if __name__ == "__main__":
    with Path(__file__).parent.joinpath('CHANGELOG-NEW.md').open('w') as file:
        file.write(format_changelog(get_changelog()))
