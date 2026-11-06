"""Write tutorial.html. Files are <pre data-file>, commands are <code class="cmd" data-run>;
tests/test_tutorial.py replays them in page order. data-run="skip" marks a command that
costs money (a real run), shown but not replayed."""
import html
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
GH = "https://github.com/teamrunner/teamrunner"
E = html.escape

parts = []


def p(text):
    parts.append(f"<p>{text}</p>")


def h2(no, title, anchor):
    parts.append(f'<h2 id="{anchor}"><span class="stepno">Step {no}</span>{title}</h2>')


def run(cmd, skip=False, expect=None):
    attrs = ' data-run="skip"' if skip else ' data-run'
    if expect:
        attrs += f' data-expect="{E(expect)}"'
    parts.append(f'<code class="cmd"{attrs}>{E(cmd)}</code>')


def file(path, text, note=None):
    cap = f'<span class="label">{E(path)}</span>' + (f'<span class="label">{E(note)}</span>' if note else "")
    marked = "" if path.startswith("~") else f' data-file="{E(path)}"'  # the key file is not replayed
    parts.append(f'<div class="panel"><div class="cap">{cap}</div>'
                 f'<pre{marked}>{E(text)}</pre></div>')


def output(text, cap="what you see"):
    parts.append(f'<div class="panel out"><div class="cap"><span class="label">{E(cap)}</span></div>'
                 f'<pre>{E(text)}</pre></div>')


def aside(text):
    parts.append(f'<div class="aside">{text}</div>')


def ul(items):
    parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")


# --- the tutorial ---------------------------------------------------------------------

parts.append('<p class="label">Tutorial</p>')
parts.append('<h1>Your first team, in ten minutes</h1>')
parts.append('<p class="lede">You will build a debate between two AI agents with a judge, '
             'run it, and then give it rounds, a fact checker and the web. No code: '
             'every step is a text file or one command.</p>')
aside('<p><b>Before you start,</b> <a href="index.html#install">install TeamRunner</a>. '
      'Every step ends with a <b>rehearsal</b>, a run with no model at all: free, and no key '
      'needed. Only step 4 calls a real model, and that is the step that needs a key.</p>')
parts.append('<nav class="toc" aria-label="Steps"><ol>'
             '<li><a href="#make">Make a team</a></li>'
             '<li><a href="#agents">Write three agents</a></li>'
             '<li><a href="#check">Check it, then rehearse it</a></li>'
             '<li><a href="#run">Run it for real</a></li>'
             '<li><a href="#rounds">Give it rounds</a></li>'
             '<li><a href="#factcheck">Add a fact checker</a></li>'
             '<li><a href="#web">Give the team the web</a></li>'
             '</ol></nav>')

h2(1, "Make a team", "make")
p("Open a terminal in any folder and make a team called <code>debate</code>:")
run("teamrunner new debate")
p("This makes a folder, <code>debate</code>, with one file in it that matters: "
  "<code>team.yaml</code>. A folder is a team when it holds a <code>team.yaml</code>. "
  "Open it in any text editor and replace what is there with this:")
file("debate/team.yaml", '''name: debate
description: Two debaters argue a topic; a judge decides

default_model: openai/gpt-6-luna

message_goes_to: topic

default_inputs:
  topic: "Remote work makes teams more productive"
''')
p("<code>default_model</code> is the model every agent in the team runs on, unless an agent "
  "names its own. <code>default_inputs</code> is what the team argues about unless you say "
  "otherwise. <code>message_goes_to</code> says that a message you give on the command line "
  "becomes the <code>topic</code>.")

h2(2, "Write three agents", "agents")
p("An agent is a Markdown file in the team's folder: settings between the <code>---</code> "
  "lines at the top, and below them the agent's instructions, in plain words. "
  "Make these three files in <code>debate</code>.")
file("debate/advocate.md", '''---
description: Argues in favor of the topic
---
You are debating in favor of this topic:

> {{topic}}

Each round, make your strongest remaining argument in one short
paragraph. From round two onward, also rebut your opponent's most
recent point before adding your own. Be persuasive but honest.
''')
file("debate/critic.md", '''---
description: Argues against the topic
---
You are debating against this topic:

> {{topic}}

Each round, rebut your opponent's most recent point, then make your
strongest remaining argument against the topic in one short paragraph.
Be persuasive but honest.
''')
file("debate/judge.md", '''---
description: Decides who argued better
output:
  winner: [advocate, critic]
  reasoning: ""
---
You have watched a debate on:

> {{topic}}

Decide which side argued better — judge argument quality and logical
clarity, not your own opinion of the topic. Announce the winner and
explain your decision in one paragraph.
''')
p("Three things to notice:")
ul(["<b>No agent names a model,</b> so all three run on the team's <code>default_model</code>. "
    "An agent that should run on another adds its own line, <code>model: …</code>, which wins. "
    "<code>teamrunner show debate/judge.md</code> prints the judge as it will run, model included.",
    "<b><code>{{topic}}</code> is filled in</b> from <code>team.yaml</code>, or from your message.",
    "<b><code>output:</code> makes the judge's verdict a fact you can count:</b> "
    "<code>winner</code> is one of two names, <code>reasoning</code> is text. "
    "TeamRunner never guesses from free text what an agent decided."])
p("There is no file saying who speaks when, so the members take one turn each, in "
  "alphabetical order: advocate, critic, judge. The folder listing is the running order.")

h2(3, "Check it, then rehearse it", "check")
p("<code>validate</code> reads every file and points at any mistake, with the line and a fix, "
  "before a single token is spent:")
run("teamrunner validate debate", expect="OK")
p("A <b>rehearsal</b> runs the whole team with no model: each member says placeholder words, "
  "and each typed answer is picked at random from what its file allows. It costs nothing and "
  "needs no key. It shows whether the flow goes where you meant, not whether the answers are good.")
run("teamrunner run debate --rehearse", expect="completed")
output('''run · debate · default input topic: "Remote work makes teams more productive"
rehearsal · no model is called; the words are placeholders and the answers random
✓ 1 model (not called)
advocate                                                     0.0s   $0.0000
    “[rehearsal] placeholder words, turn 1.”
critic                                                       0.0s   $0.0000
    “[rehearsal] placeholder words, turn 2.”
judge                       winner = critic                  0.0s   $0.0000
    “[rehearsal] placeholder words, turn 3.”

completed · 3 turns · 0.1s · ≈ $0.0000
runs/2026-11-05_093012_debate''')

h2(4, "Run it for real", "run")
p("Put your OpenAI key in TeamRunner's key file, <code>~/.teamrunner/.env</code>, in your home "
  "folder and never inside a team (team folders get shared, and a key would go with them). "
  "If the key is already set in your terminal, TeamRunner offers to save it the first time.")
file("~/.teamrunner/.env", "OPENAI_API_KEY=sk-...\n", note="in your home folder")
p("Then run the debate, on its default topic or on one you give:")
run("teamrunner run debate", skip=True)
run('teamrunner run debate --message "Four-day weeks make teams more productive"', skip=True)
p("Each turn shows who spoke, what they decided, how long it took and what it cost; a run like "
  "this costs a fraction of a cent. Every run is kept in <code>debate/runs/</code>: everything "
  "said, every prompt, the model that answered, and the cost. To see them all, newest first:")
run("teamrunner runs debate", expect="debate")
aside("<p>Other providers work the same way: change <code>default_model:</code> to "
      "<code>anthropic/…</code> or <code>gemini/…</code> and put that provider's key in the same file. "
      "Free local models work too, through <a href=\"https://ollama.com\">Ollama</a>: "
      "<code>ollama/llama3.2</code>.</p>")

h2(5, "Give it rounds", "rounds")
p("A real debate has rounds. Who acts when is the job of the team's <b>chair</b>, a file called "
  "<code>chair.md</code> holding the meeting's script. Add it:")
file("debate/chair.md", '''# Three rounds of advocate and critic, then the judge decides.

rounds(*3) -> judge

rounds = advocate -> critic
''')
p("<code>a -> b</code> means one after the other, <code>rounds(*3)</code> repeats a step three "
  "times, and <code>rounds = …</code> says what that step is. Lines starting with <code>#</code> "
  "are notes for people. Now the debate runs advocate, critic three times over, then the judge.")
run("teamrunner run debate --rehearse", expect="7 turns")
p("To read the flow back in plain English, or as a picture in your browser:")
run("teamrunner explain debate", expect="judge")
run("teamrunner explain debate --diagram", skip=True)

h2(6, "Add a fact checker", "factcheck")
p("Suppose each speech should be fact-checked before it stands. A fact checker is one more agent, "
  "whose <code>output:</code> is a verdict:")
file("debate/fact_checker.md", '''---
description: Checks the factual claims in the latest speech
output:
  verdict: [pass, fail]
  reasons: ""
---
You are a neutral fact checker in a formal debate. Examine the latest
speech for checkable factual claims and verify them by searching the
web (ask the web toolkeeper). Search only for claims you cannot confirm
from what you know; most speeches need one or two searches. Minor
exaggeration is fine; invented statistics, misattributed quotes and
false claims are not.

Set verdict to fail only if a claim is materially false, and list each
false claim with a one-line correction in reasons. Otherwise set it to
pass.
''')
p("The chair decides what each verdict means. Replace <code>chair.md</code> with:")
file("debate/chair.md", '''# Three rounds. Each speech is fact-checked; a failed speech gets two
# more tries, then the debate moves on. Then the judge decides.

rounds(*3) -> judge

rounds = advocate_turn -> critic_turn

advocate_turn = advocate -> fact_checker
                fact_checker --fail--> advocate
                fact_checker --pass,*3--> done

critic_turn = critic -> fact_checker
              fact_checker --fail--> critic
              fact_checker --pass,*3--> done
''')
p("<code>--fail--> advocate</code> sends a failed speech back. <code>--pass,*3--> done</code> "
  "reads “on pass, or the third time, this turn is done”: every loop needs a limit, so a debate "
  "always ends. The fact checker's file says how to judge; the chair says what its verdict means "
  "here, which is why the same fact checker serves both sides.")
run("teamrunner validate debate", expect="OK")
run("teamrunner run debate --rehearse", expect="completed")
aside("<p>Mistype an option, say <code>--puss--></code>, and <code>validate</code> stops you: "
      "“<code>puss</code> is not one of <code>fact_checker</code>'s options; did you mean "
      "<code>pass</code>?”</p>")

h2(7, "Give the team the web", "web")
p("Agents never hold tools themselves. A tool sits with a <b>toolkeeper</b>, a member with no "
  "model that checks who is asking and enforces the limits, like the attendant at a tool crib. "
  "Add one for web search:")
file("debate/web.md", '''---
description: The web toolkeeper — searches the web, on different terms for different members
kind: toolkeeper
tools:
  web_search_brave: {max_results: 5, calls_per_turn: 2}   # the base terms
access:
  fact_checker: {calls_per_turn: 3}   # a few claims a speech may need checking
  judge: standard                     # the base terms
---
I search the web. Send me a search query and I return the top five
results with their sources.
''')
ul(["<b><code>tools:</code></b> names the tool and its base terms: five results, two searches a turn.",
    "<b><code>access:</code></b> lists who may use it. The fact checker may search three times a turn; "
    "the judge gets the base terms; the debaters, not listed, argue from what they know.",
    "<b>The text below</b> is what the members who may use it are told about it."])
p("Nothing in the chair mentions <code>web</code>: during its turn the fact checker may search, "
  "up to its limit, or not at all. Every request, the toolkeeper's yes or no, and the search are "
  "logged. <code>explain</code> prints who may use what, on which terms:")
run("teamrunner run debate --rehearse", expect="completed")
run("teamrunner explain debate", expect="web_search_brave")
aside("<p>For real searches, add a <a href=\"https://brave.com/search/api/\">Brave Search API</a> "
      "key to the same key file as <code>BRAVE_API_KEY</code>. A search costs half a cent at "
      "Brave's list price, and a run's cost counts it.</p>")

parts.append('<h2 id="next">Where to go next</h2>')
ul(["<b>Start from an example.</b> Six ship with TeamRunner; "
    "<code>teamrunner new my_team --from fact_checked</code> copies the finished version of this "
    "tutorial, with a Python sandbox too. <a href=\"index.html#examples\">See all six</a>.",
    f"<b>Read the reference.</b> Every file and every word a team may use is in the "
    f"<a href=\"{GH}#readme\">documentation</a>.",
    f"<b>Tell us what you found.</b> <a href=\"{GH}/issues/new/choose\">Open an issue</a>, or "
    "write to hello@teamrunner.ai."])

# --- the page --------------------------------------------------------------------------

home = pathlib.Path(out.parent, "index.html").read_text()
head = home[:home.index("<title>")]
mark = home[home.index("<svg"):home.index("</svg>") + len("</svg>")]
page = (head
        + "<title>Tutorial — TeamRunner</title>\n"
        + '<meta name="description" content="Build a team of AI agents from text files in ten minutes: '
          'a debate with a judge, rounds, a fact checker and the web. No code.">\n'
        + '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        + '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        + '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        + home[home.index('<link rel="stylesheet" href="https://fonts'):home.index('<link rel="stylesheet" href="site.css">')]
        + '<link rel="stylesheet" href="site.css">\n</head>\n<body>\n'
        + f'''<header class="top">
  <div class="wrap">
    <a class="mark" href="index.html" aria-label="TeamRunner home">
      {mark}
      teamrunner
    </a>
    <nav aria-label="Main">
      <a href="index.html#install">Install</a>
      <a href="tutorial.html" aria-current="page" style="color:var(--ink)">Tutorial</a>
      <a href="index.html#concepts">Concepts</a>
      <a href="index.html#examples">Examples</a>
      <a href="index.html#reference">Reference</a>
    </nav>
    <div class="right">
      <span class="pill">preview 0.0.2</span>
      <a class="pill" href="{GH}">GitHub</a>
    </div>
  </div>
</header>
<main class="doc">
'''
        + "\n".join(parts)
        + '''
<div class="nextprev"><a href="index.html">← Home</a><a href="index.html#examples">The examples →</a></div>
</main>
</body>
</html>
''')
out.write_text(page)
print("wrote", out, len(page), "bytes")
