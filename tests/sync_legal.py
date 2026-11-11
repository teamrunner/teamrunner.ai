"""Copy canonical package notices into the static website.

Run from this workspace before publishing either repository:
    python tests/sync_legal.py /path/to/teamrunner
    python tests/sync_legal.py /path/to/teamrunner --check
No network access or publication is performed.
"""
from pathlib import Path
import argparse
import html
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('package', type=Path)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
site = Path(__file__).resolve().parents[1]
package = args.package.resolve()
source = (package / 'LEGAL.md').read_text(encoding='utf-8')

def paragraph(text):
    text = html.escape(text)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

blocks = []
for block in source.strip().split('\n\n'):
    if block.startswith('# '):
        blocks.append('<h1>' + html.escape(block[2:]) + '</h1>')
    elif block.startswith('## '):
        blocks.append('<h2>' + html.escape(block[3:]) + '</h2>')
    else:
        blocks.append('<p>' + paragraph(block.replace('\n', ' ')) + '</p>')
home = (site / 'index.html').read_text(encoding='utf-8')
head = home[:home.index('<title>')]
header = home[home.index('<header'):home.index('</header>') + len('</header>')]
footer = home[home.index('<footer>'):home.index('</footer>') + len('</footer>')]
website = '''<h2 id="website-data">Website data</h2>
<p>This website is hosted on GitHub Pages. Page visits and selected actions are
counted through GoatCounter without analytics cookies. The site loads font
styles and files from Google Fonts. Those services receive network requests
and have their own data practices; this is not a promise of anonymous browsing.</p>
<p>News signup sends your email address and the signup page to a Google Apps
Script service operated for TeamRunner. It stores the address, signup time and
page in our Google Sheet. We use the list for TeamRunner updates. Every update
has an unsubscribe option; email hello@teamrunner.ai to request removal.</p>
<p>The recorded debates on the homepage are replays, not live model calls.
Their original records retain the file names and cost estimates from the
version that produced them. Running a team locally can send inputs to the
services described above.</p>
<h2>License copies and third-party materials</h2>
<p>The original website code and documentation are GPL-3.0-or-later, with
third-party materials retaining their own rights. This does not grant rights
to the TeamRunner name or imply endorsement.</p>
<p><a href="LICENSE">GPL license, warranty and liability terms</a> ·
<a href="templates-LICENSE">MIT-0 examples and authoring guide license</a> ·
<a href="NOTICE">Package third-party notices</a> ·
<a href="WEBSITE-NOTICE">Website notices</a></p>
<p>Fonts are loaded from Google Fonts: IBM Plex Sans, IBM Plex Mono and
Newsreader, under the SIL Open Font License 1.1. They retain their respective
copyrights. Hosting, analytics, email services, model providers and public
sources have their own terms and data practices.</p>'''
page = (head + '<title>Publisher, licenses and data notices — TeamRunner</title>\n'
        '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        '<link rel="stylesheet" href="site.css">\n</head>\n<body>\n' + header
        + '\n<main class="doc">\n' + '\n'.join(blocks) + '\n' + website
        + '\n</main>\n' + footer + '\n</body>\n</html>\n')
outputs = {
    site / 'legal.html': page,
    site / 'LICENSE': (package / 'LICENSE').read_text(encoding='utf-8'),
    site / 'templates-LICENSE': (package / 'examples/LICENSE').read_text(encoding='utf-8'),
    site / 'NOTICE': (package / 'NOTICE').read_text(encoding='utf-8'),
}
failed = []
for target, content in outputs.items():
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            failed.append(target.name)
    else:
        target.write_text(content, encoding='utf-8')
if failed:
    parser.exit(1, 'Out of date: ' + ', '.join(failed) + '\n')
print('Website notices match the package.' if args.check else 'Updated website notices from the package.')
