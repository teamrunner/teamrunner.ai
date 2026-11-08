"""Write tutorial.html. Files are <pre data-file>, edits are <div class="diff" data-edit>,
commands are <code class="cmd" data-run>; tests/test_tutorial.py replays them in page order.
data-run="skip" marks a command that costs money (a real run) or opens a browser, shown
but not replayed.

Each step's "do this" part comes twice (D137): in <div class="via" data-via="browser">,
naming the page's buttons as <b class="ui">, and in <div class="via" data-via="terminal">,
holding the commands the test replays. Files and diffs are the same either way, so they
stay outside both. The test also checks that every <b class="ui"> label is in the files of
`teamrunner ui`, so a renamed button fails it. Screenshots are in img/, retaken with
tests/screenshots.py.

Every step starts from an example that ships with TeamRunner. The examples name their
model differently from one version to the next, so the tutorial never rewrites a whole
member file: it changes the lines it shows, as a diff, and works whichever version
copied the example.

    python tests/build_tutorial.py tutorial.html
"""
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
    parts.append('<div class="via-switch" role="group" aria-label="Follow this tutorial">'
                 '<span>follow in</span>'
                 '<button type="button" data-via="browser" aria-pressed="true">Browser</button>'
                 '<button type="button" data-via="terminal" aria-pressed="false">Terminal</button></div>')


def run(cmd, skip=False, expect=None):
    attrs = ' data-run="skip"' if skip else ' data-run'
    if expect:
        attrs += f' data-expect="{E(expect)}"'
    parts.append(f'<code class="cmd"{attrs}>{E(cmd)}</code>')


def shell(cmd):
    """A command that is not TeamRunner's (a loop, a file listing): shown, never replayed."""
    parts.append(f'<code class="cmd">{E(cmd)}</code>')


def file(path, text, note=None):
    cap = f'<span class="label">{E(path)}</span>' + (f'<span class="label">{E(note)}</span>' if note else "")
    marked = "" if path.startswith("~") else f' data-file="{E(path)}"'  # the key file is not replayed
    parts.append(f'<div class="panel"><div class="cap">{cap}</div>'
                 f'<pre{marked}>{E(text)}</pre></div>')


def show(path, text, note=None):
    """Part of a file, to read: shown, never written."""
    cap = f'<span class="label">{E(path)}</span>' + (f'<span class="label">{E(note)}</span>' if note else "")
    parts.append(f'<div class="panel"><div class="cap">{cap}</div><pre>{E(text)}</pre></div>')


def edit(path, rows, note="change these lines"):
    """A change to a file, as a diff: rows of ("-", old line), ("+", new line), (" ", context)."""
    cls = {"-": "m", "+": "p", " ": "x"}
    lines = "".join(f'<div class="{cls[k]}">{E(k + " " + t)}</div>' for k, t in rows)
    parts.append(f'<div class="panel"><div class="cap"><span class="label">{E(path)}</span>'
                 f'<span class="label">{E(note)}</span></div>'
                 f'<div class="diff" data-edit="{E(path)}">{lines}</div></div>')


def output(text, cap="what you see"):
    parts.append(f'<div class="panel out"><div class="cap"><span class="label">{E(cap)}</span></div>'
                 f'<pre>{E(text)}</pre></div>')


def aside(text):
    parts.append(f'<div class="aside">{text}</div>')


def ul(items):
    parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")


def tip(word, meaning):
    return f'<a class="t" tabindex="0" data-tip="{E(meaning)}">{word}</a>'


def ui(label):
    """A button or field on the page, by the name it shows there."""
    return f'<b class="ui">{E(label)}</b>'


def shot(name, alt, caption):
    parts.append(f'<figure class="shot"><img src="img/{name}" alt="{E(alt)}" width="1240" '
                 f'height="780" loading="lazy"><figcaption>{caption}</figcaption></figure>')


class via:
    """with via("browser"): ... — the parts written inside belong to that way of following."""

    def __init__(self, how):
        self.how = how

    def __enter__(self):
        parts.append(f'<div class="via" data-via="{self.how}">')

    def __exit__(self, *_):
        parts.append("</div>")


STEPS = [
    ("rehearse", "Rehearse a team, for free"),
    ("first-run", "Your first real run"),
    ("prose", "Edit the words"),
    ("flow", "Take control of the flow"),
    ("decisions", "Typed answers and decisions"),
    ("tools", "Tools, through a toolkeeper"),
    ("private", "Private information"),
    ("experiment", "A first experiment, by hand"),
    ("bigger", "Bigger organizations"),
]

TERMINAL = tip("terminal", "The window where you type commands: Terminal on a Mac, PowerShell on "
               "Windows. You type a line and press Return.")

# --- the tutorial ---------------------------------------------------------------------

parts.append('<p class="label">Tutorial</p>')
parts.append('<h1>Nine steps, from a free rehearsal to your first experiment</h1>')
parts.append('<p class="lede">Every step starts from a team that ships with TeamRunner and adds '
             'one idea. No code: each step is a few words changed in a text file, and a click or '
             'a command.</p>')
aside('<p><b>Before you start,</b> <a href="install.html">install TeamRunner</a> (version '
      '0.0.4 or later for the browser). Follow each step <b>in your browser</b>, on TeamRunner\'s '
      'own page, or <b>in a ' + TERMINAL + '</b> with any text editor: the switch at each step '
      'changes them all. The files you write are the same either way. Step 1 needs no key and '
      'costs nothing, and every later step can be <b>rehearsed</b> for free before you spend '
      'anything. A real run costs a fraction of a cent.</p>')
parts.append('<nav class="toc" aria-label="Steps"><ol>'
             + "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in STEPS) + '</ol></nav>')

# 1 ------------------------------------------------------------------------------------
h2(1, "Rehearse a team, for free", "rehearse")
with via("browser"):
    p("Open a " + TERMINAL + " in the folder where you want to keep your teams, and open "
      "TeamRunner's page. This is the one command you need:")
    run("teamrunner ui", skip=True)
    p("A tab opens in your browser. Keep the terminal open while you work; "
      "<code>Ctrl+C</code> there closes the page. The page works only on your computer, on the "
      "files in that folder.")
    p("Copy the simplest example, <code>round_robin</code>, into a new team called "
      "<code>hello</code>: choose " + ui("New team") + ", type <code>hello</code>, pick "
      "<code>round_robin</code> under " + ui("Start from") + " and choose " + ui("Continue") + ".")
with via("terminal"):
    p("Open a terminal in any folder and copy the simplest example, <code>round_robin</code>, into "
      "a new team called <code>hello</code>:")
    run("teamrunner new hello --from round_robin", expect="hello")
p("<code>hello</code> is a folder of four text files. <code>team.yaml</code> says what the team "
  "is for, and each <code>.md</code> file is one agent: a debater for the topic, one against, and "
  "a judge. Open <code>hello/02_against.md</code>, on the left of the page or in your text editor:")
show("hello/02_against.md", "---\ndescription: Argues against the topic\n…\n---\n"
     "You are debating against this topic:\n\n> {{topic}}\n\n"
     "You speak once, after your opponent. Rebut their main point, then make\n"
     "your strongest case against the topic, in one paragraph.\n", note="part of it")
p("Between the two <code>---</code> lines are the agent's settings (its "
  + tip("frontmatter", "The settings block between the two --- lines at the top of an agent's "
        "file: a description, which model, what answer it must give.")
  + "). Below them are its instructions, in plain words. <code>{{topic}}</code> is filled in "
  "with the topic in <code>team.yaml</code>.")
p("Now <b>rehearse</b> the team: run all of it with no model. Each agent says placeholder words, "
  "and the judge's answer is picked at random. It costs nothing and needs no key, and it shows "
  "whether the team runs the way you meant.")
with via("browser"):
    p("Choose " + ui("Run…") + ", keep " + ui("Rehearse (free, no model)") + " ticked, and choose "
      + ui("Rehearse team") + ". The conversation appears turn by turn, and stays under "
      + ui("Runs") + " afterwards:")
    shot("ui-conversation.png", "TeamRunner's page showing a rehearsal of hello: completed, "
         "3 turns, $0.0000, and the first turn, for, with placeholder words",
         "A rehearsal in " + ui("Runs") + ": every turn, what each member could read, and the cost.")
with via("terminal"):
    run("teamrunner run hello --rehearse", expect="completed")
    output("""run · hello · default input topic: "Remote work makes teams more productive"
rehearsal · no model is called; the words are placeholders and the answers random
for                                                          0.0s   $0.0000
    “[rehearsal] placeholder words, turn 1.”
against                                                      0.0s   $0.0000
    “[rehearsal] placeholder words, turn 2.”
judge                       winner = for                     0.0s   $0.0000
    “[rehearsal] placeholder words, turn 3.”

completed · 3 turns · 0.0s · ≈ $0.0000
hello/runs/2026-11-05_093012_hello""")
p("There is no file saying who speaks when, so each member takes one turn, in the order of their "
  "file names: <code>01_for</code>, <code>02_against</code>, <code>03_judge</code>. The numbers "
  "set the order and are not part of the names.")

# 2 ------------------------------------------------------------------------------------
h2(2, "Your first real run", "first-run")
p("A real run calls a model, which needs an "
  + tip("API key", "A password-like code from a model provider that lets TeamRunner use its "
        "models. The provider bills you for what you use.")
  + ": a code from the model's provider that lets TeamRunner use it, billed by the provider. "
  "The model is named once, as <code>default_model:</code> in <code>hello/team.yaml</code>.")
with via("browser"):
    p("Select <code>team.yaml</code> to see it. Then try a real run: choose " + ui("Run…")
      + ", clear " + ui("Rehearse (free, no model)") + " and choose " + ui("Run with models")
      + ". If the key is missing, TeamRunner stops before anything is spent and tells you which "
      "key it needs.")
with via("terminal"):
    p("<code>explain</code> shows it beside each member:")
    run("teamrunner explain hello", expect="for")
    p("Try a real run. If the key is missing, TeamRunner stops before anything is spent and tells "
      "you which key it needs:")
    run("teamrunner run hello", skip=True)
    output("""✗ the run cannot start:
  OPENROUTER_API_KEY   for, against and judge use openrouter/google/gemma-4-31b-it,
                       which needs OPENROUTER_API_KEY; not found in ~/.teamrunner/.env,
                       your shell or the package
                       add `OPENROUTER_API_KEY=…` to ~/.teamrunner/.env""", cap="without a key")
p("The examples run on Gemma 4 through <a href=\"https://openrouter.ai\">OpenRouter</a>, one key "
  "for many providers' models. Make an account there, add a few dollars of credit and create a "
  "key. TeamRunner keeps keys in one file, <code>~/.teamrunner/.env</code>: a file called "
  "<code>.env</code> in a folder called <code>.teamrunner</code> in your home folder. It is never "
  "inside a team, because team folders get shared and a key would go with them. One key is all "
  "you need.")
with via("browser"):
    p("Choose " + ui("Set up keys") + ", pick <code>OPENROUTER_API_KEY</code>, paste the key into "
      + ui("New key") + " and choose " + ui("Save key") + ". The page writes it to that file and "
      "never shows it again; " + ui("Check keys and models online") + " checks that it works.")
with via("terminal"):
    p("Put your key in it:")
    file("~/.teamrunner/.env", "OPENROUTER_API_KEY=sk-or-...\n", note="in your home folder")
with via("browser"):
    p("Run it again, and this time give it your own topic: in " + ui("Run…") + ", choose "
      + ui("A message") + " under " + ui("What to give the team") + " and type "
      "<code>Four-day weeks make teams more productive</code>. The message fills in "
      "<code>{{topic}}</code>. Tick " + ui("Rehearse (free, no model)") + " to try a message for "
      "free.")
with via("terminal"):
    p("Run it again, and this time give it your own topic. <code>--message</code> fills in "
      "<code>{{topic}}</code>:")
    run('teamrunner run hello --message "Four-day weeks make teams more productive"', skip=True)
    p("You can rehearse with a message too, for free:")
    run('teamrunner run hello --rehearse --message "Four-day weeks make teams more productive"',
        expect="Four-day weeks")
p("Every run is kept in <code>hello/runs/</code>, one folder each, named for when it ran. Its "
  "<code>output.md</code> is what the team produced. Next to it, <code>events.jsonl</code> holds "
  "every turn, with every prompt, reply, model, token and cost.")
with via("browser"):
    p(ui("Runs") + " lists them, newest first, with each verdict. Select one to read its "
      + ui("Conversation") + ", its " + ui("Output") + " and its " + ui("Record") + "; the "
      "links beside them open the files themselves.")
with via("terminal"):
    p("Open the newest one's <code>output.md</code> in your text editor. To list the runs, "
      "newest first, with each verdict:")
    run("teamrunner runs hello", expect="winner")
    p("And to see the newest one again, as it printed:")
    run("teamrunner runs hello latest", expect="judge")
aside("<p><b>Another provider, or free local models?</b> Change <code>default_model:</code> to "
      "<code>openai/…</code>, <code>anthropic/…</code> or <code>gemini/…</code> and add that "
      "provider's key instead. Free "
      "models on your own computer work too, through <a href=\"https://ollama.com\">Ollama</a>: "
      "<code>ollama/gpt-oss:20b</code>. Pick one of about 20 billion parameters or more: the "
      "smallest models often can't give answers in the form a team needs.</p>")
aside("<p><b>Or describe a team in a sentence,</b> and a model writes the files for you. It "
      "costs a cent or two, and you can rehearse what it wrote for free. In a terminal:</p>"
      '<code class="cmd" data-run="skip">teamrunner new launch --describe "A product manager '
      'pitches a feature. An engineer and a designer push back, twice. Then the CEO decides go '
      'or no-go."</code>')

# 3 ------------------------------------------------------------------------------------
h2(3, "Edit the words", "prose")
p("Everything an agent does comes from its words. Make the critic more aggressive: in "
  "<code>hello/02_against.md</code>, replace the last two lines with these. In this view, red "
  "is a line to remove and green a line to add; it is called a "
  + tip("diff", "A view of what changed between two versions of a file: removed lines in red, "
        "added lines in green.") + ".")
edit("hello/02_against.md", [
    ("-", "You speak once, after your opponent. Rebut their main point, then make"),
    ("-", "your strongest case against the topic, in one paragraph."),
    ("+", "You speak once, after your opponent. Attack their weakest claim"),
    ("+", "directly and without hedging: name it, say why it fails, and give"),
    ("+", "the strongest counter-evidence you know. Then make your case against"),
    ("+", "the topic, in one forceful paragraph."),
])
with via("browser"):
    p(ui("Save") + " (Ctrl+S, or ⌘S on a Mac). Rehearse to check nothing broke, then run it with "
      "models on the same message as before.")
    p("Now compare. In " + ui("Runs") + ", tick the two real runs and choose "
      + ui("Compare selected runs") + ": their outputs side by side, and under "
      + ui("Member versions") + ", the paragraph you changed.")
    shot("ui-compare.png", "Two runs of hello compared: for and judge unchanged, against changed "
         "from version 1 to version 2, with the removed and added lines",
         "Two runs compared: TeamRunner numbers each member's versions and shows what changed.")
with via("terminal"):
    p("Rehearse to check nothing broke, then run it for real on the same topic as before:")
    run("teamrunner run hello --rehearse", expect="completed")
    run('teamrunner run hello --message "Four-day weeks make teams more productive"', skip=True)
    p("Now compare. <code>teamrunner runs hello</code> lists both real runs with their verdicts. "
      "Open the two <code>output.md</code> files side by side: same team, same topic, one "
      "paragraph changed.")
p("Did the judge decide differently? With one run of each you can't tell whether the words did "
  "it or chance did; models are random. Step 8 deals with that.")

# 4 ------------------------------------------------------------------------------------
h2(4, "Take control of the flow", "flow")
p("A real debate has rounds. Who acts when is the job of the team's <b>chair</b>, a file called "
  "<code>chair.md</code> holding the meeting's script. Make <code>hello/chair.md</code> with "
  "these lines:")
with via("browser"):
    p("With a file of <code>hello</code> selected, choose " + ui("New member") + ", name it "
      "<code>chair.md</code>, and replace what is in it with the lines below.")
file("hello/chair.md", "# Three rounds of for and against, then the judge decides.\n\n"
     "rounds(*3) -> judge\n\nrounds = for -> against\n")
p("<code>a -> b</code> means one after the other, <code>rounds(*3)</code> repeats a step three "
  "times, and <code>rounds = …</code> says what that step is. Lines starting with <code>#</code> "
  "are notes for people. Rehearse it: seven turns now, where there were three.")
with via("browser"):
    p(ui("Save") + ", then rehearse with " + ui("Run…") + ". " + ui("Flow diagram") + " draws the "
      "flow, and reads the team back in plain words below it:")
    shot("ui-flow.png", "The flow diagram of hello/chair.md: for then against, three times, then "
         "judge", "The chair's script as a picture. Save an edit and it is redrawn.")
with via("terminal"):
    run("teamrunner run hello --rehearse", expect="7 turns")
    p("<code>explain</code> reads the team back in plain words, or draws the flow in your browser:")
    run("teamrunner explain hello", expect="rounds")
    run("teamrunner explain hello --diagram", skip=True)
p("The debaters' words still say they speak once. The example <code>multi_agent_debate</code> is "
  "this team finished, with words written for rounds. Copy it into a team called "
  "<code>debate</code>; the next step builds on it.")
with via("browser"):
    p(ui("New team") + ", <code>debate</code>, from <code>multi_agent_debate</code>, and look at "
      "its " + ui("Flow diagram") + ".")
with via("terminal"):
    run("teamrunner new debate --from multi_agent_debate", expect="debate")
    run("teamrunner explain debate", expect="rounds")

# 5 ------------------------------------------------------------------------------------
h2(5, "Typed answers and decisions", "decisions")
p("Look at the top of <code>debate/judge.md</code>:")
show("debate/judge.md", "---\ndescription: Decides who argued better\noutput:\n"
     "  winner: [for, against]\n  reasoning: \"\"\n…\n---", note="its settings")
p("<code>output:</code> makes the judge's verdict a fact you can count: <code>winner</code> is one "
  "of the names in the brackets, and <code>reasoning</code> is text. TeamRunner never guesses from "
  "free text what an agent decided. Allow a tie:")
edit("debate/judge.md", [("-", "  winner: [for, against]"), ("+", "  winner: [for, against, tie]")])
p("TeamRunner <b>validates</b> a team: it reads every file and points at any mistake, with the "
  "line and a fix, before a single token is spent. Then rehearse.")
with via("browser"):
    p(ui("Save") + ", and the page validates for you: any problem appears under "
      + ui("Validation") + ", and selecting it opens the file at that line. Then rehearse with "
      + ui("Run…") + ".")
with via("terminal"):
    run("teamrunner validate debate", expect="OK")
    run("teamrunner run debate --rehearse", expect="winner")
p("A typed answer can also <b>decide what happens next</b>. The example <code>fact_checked</code> "
  "is the debate with a fact checker, whose answer is <code>verdict: [pass, fail]</code>. Copy it "
  "into a team called <code>checked</code>:")
with via("browser"):
    p(ui("New team") + ", <code>checked</code>, from <code>fact_checked</code>.")
with via("terminal"):
    run("teamrunner new checked --from fact_checked", expect="checked")
p("In its <code>chair.md</code>, each speech goes to the fact checker, and a failed speech goes "
  "back to its speaker:")
show("checked/chair.md", "for_turn = for -> fact_checker\n"
     "           fact_checker --fail--> for\n"
     "           fact_checker --pass,*3--> done", note="part of it")
p("<code>--fail--> for</code> sends a failed speech back. <code>--pass,*3--> done</code> reads "
  "“on pass, or the third time, this turn is done”: every loop needs a limit, so a debate always "
  "ends. Give each speaker one retry instead of two. The same line appears for both sides, and "
  "the change applies to both:")
edit("checked/chair.md", [("-", "fact_checker --pass,*3--> done"), ("+", "fact_checker --pass,*2--> done")],
     note="in both places")
with via("browser"):
    p(ui("Save") + ", check " + ui("Validation") + ", and rehearse.")
with via("terminal"):
    run("teamrunner validate checked", expect="OK")
    run("teamrunner run checked --rehearse", expect="completed")
aside("<p>Mistype an answer, say <code>--puss--></code>, and validation stops you: "
      "“<code>puss</code> is not one of <code>fact_checker</code>'s options; did you mean "
      "<code>pass</code>?”</p>")

# 6 ------------------------------------------------------------------------------------
h2(6, "Tools, through a toolkeeper", "tools")
p("Agents never hold tools themselves. A tool sits with a "
  + tip("toolkeeper", "A member with no model that holds one tool and decides who may use it and "
        "how often, like the attendant at a factory's tool crib.")
  + ": a member with no model that checks who is asking and enforces the limits, like the "
  "attendant at a tool crib. In <code>checked</code>, <code>web.md</code> holds the web, and its "
  "<code>access:</code> list says who may use it:")
show("checked/web.md", "kind: toolkeeper\n…\naccess:\n  fact_checker: {calls_per_turn: 3}\n"
     "  judge: standard", note="part of its settings")
p("The fact checker may use it three times a turn; the judge on the standard terms; the "
  "debaters, not listed, argue from what they know. Give the side arguing <i>for</i> the web too, "
  "once a turn, and the debate is no longer even:")
edit("checked/web.md", [(" ", "access:"), ("+", "  for: {calls_per_turn: 1}")], note="add a line")
with via("browser"):
    p(ui("Save") + ". The plain-words summary under " + ui("Flow diagram") + " says who may use "
      "what, on which terms. Then rehearse.")
with via("terminal"):
    p("<code>explain</code> prints who may use what, on which terms:")
    run("teamrunner explain checked", expect="for may use it")
    run("teamrunner run checked --rehearse", expect="completed")
p("Every request, the toolkeeper's yes or no, and what came back are kept in the run. "
  "<code>checked</code> also has a second toolkeeper, <code>sandbox.md</code>, which runs Python "
  "so the fact checker can check the sums in a claim.")

# 7 ------------------------------------------------------------------------------------
h2(7, "Private information", "private")
p("So far everyone knows the same things. The example <code>hiring_committee</code> is a "
  "committee choosing a Director of Operations, where each member also knows two facts the "
  "others don't. Copy it into a team called <code>committee</code>:")
with via("browser"):
    p(ui("New team") + ", <code>committee</code>, from <code>hiring_committee</code>.")
with via("terminal"):
    run("teamrunner new committee --from hiring_committee", expect="committee")
p("What everyone has read, the application packet, is in <code>team.yaml</code>. What only one "
  "member knows is written into that member's own file:")
show("committee/chen.md", "You also sat in on the reference calls, and your notes say:\n\n"
     "- Asked whether they would hire Avery again, Avery's former manager\n"
     "  said only that it was company policy not to comment.\n"
     "- Blake's former manager said Blake was the best operations person\n"
     "  they had worked with.\n\nThe others have not seen your notes.", note="part of it")
p("The others learn Chen's notes only if Chen says them in the meeting. Each member answers "
  "<code>preferred</code> every turn, whom they would hire right now, so you can see when minds "
  "change; the clerk records the <code>decision</code>. Rehearse it, then run it for real.")
with via("browser"):
    p(ui("Run…") + " twice: once rehearsed, once " + ui("Run with models") + ". " + ui("Runs")
      + " shows each run's decision.")
with via("terminal"):
    run("teamrunner run committee --rehearse", expect="completed")
    run("teamrunner run committee", skip=True)
    run("teamrunner runs committee", expect="decision")
p("The packet makes Avery look best; the six private facts together make Blake the clear "
  "choice. In 1985 Stasser and Titus found that human groups mostly discuss what they all "
  "already know, and pick Avery. What did your committee do?")

# 8 ------------------------------------------------------------------------------------
h2(8, "A first experiment, by hand", "experiment")
p("A known fix is to have everyone report what they know before anyone gives an opinion. "
  "Compare it with open discussion: make two copies of the committee, <code>open</code> and "
  "<code>share_first</code>, one for each way of running the meeting.")
with via("browser"):
    p(ui("New team") + " twice, both from <code>hiring_committee</code>: <code>open</code> and "
      "<code>share_first</code>.")
with via("terminal"):
    run("teamrunner new open --from hiring_committee", expect="open")
    run("teamrunner new share_first --from hiring_committee", expect="share_first")
p("Both ways are already written in <code>chair.md</code>, one turned off with a <code>#</code>. "
  "In <code>share_first/chair.md</code>, swap them: put a <code>#</code> in front of the first "
  "line and take it off the second.")
edit("share_first/chair.md", [
    ("-", "meeting(*3) -> clerk:record"),
    ("+", "# meeting(*3) -> clerk:record"),
    (" ", "#"),
    (" ", "# Share first: the chair asks each member to report what they know"),
    (" ", "# before anyone gives an opinion, then two rounds of discussion. Put a"),
    (" ", "# `#` in front of the line above and remove it from the line below."),
    ("-", "# chen:share_facts -> diaz:share_facts -> okafor:share_facts -> meeting(*2) -> clerk:record"),
    ("+", "chen:share_facts -> diaz:share_facts -> okafor:share_facts -> meeting(*2) -> clerk:record"),
])
with via("browser"):
    p(ui("Save") + ", check " + ui("Validation") + ", and rehearse both teams.")
with via("terminal"):
    run("teamrunner validate share_first", expect="OK")
    run("teamrunner run open --rehearse", expect="10 turns")
    run("teamrunner run share_first --rehearse", expect="share_facts")
p("Models are random, so one run of each proves nothing. Run each five times, then tally: count "
  "how often each committee chose Blake. Ten real runs cost a few cents.")
with via("browser"):
    p("The page runs one team at a time, so start each run when the last one has finished: "
      + ui("Run…") + " with models, five times on <code>open</code> and five on "
      "<code>share_first</code>. Then, in " + ui("Runs") + ", pick each team under "
      + ui("Team") + " and count the decisions.")
with via("terminal"):
    p("On a Mac or Linux:")
    shell("for i in 1 2 3 4 5; do teamrunner run open; teamrunner run share_first; done")
    p("In PowerShell on Windows:")
    shell("1..5 | % { teamrunner run open; teamrunner run share_first }")
    p("Each list shows every run's decision:")
    run("teamrunner runs open", expect="decision")
    run("teamrunner runs share_first", expect="decision")
aside('<p><b>Coming soon: experiments.</b> One file will name both versions and how many runs '
      'of each, and TeamRunner will run them all and give you one CSV for R, Stata or pandas. '
      '<a href="index.html#coming">What it will look like</a>.</p>')

# 9 ------------------------------------------------------------------------------------
h2(9, "Bigger organizations", "bigger")
p("Two larger examples show how far the same few ideas go. <code>orchestrators_lite</code> is "
  "five engineers reviewing code with planted bugs, in rounds, one of them writing the report. "
  "All five share one model profile in <code>models/</code>, so changing the model there "
  "changes it for everyone. Copy it into a team called <code>review</code>, read it back and "
  "rehearse it:")
with via("browser"):
    p(ui("New team") + ", <code>review</code>, from <code>orchestrators_lite</code>; then "
      + ui("Flow diagram") + " and a rehearsal.")
with via("terminal"):
    run("teamrunner new review --from orchestrators_lite", expect="review")
    run("teamrunner explain review", expect="emma")
    run("teamrunner run review --rehearse", expect="completed")
p("<code>reference_check</code> checks every reference in a paper: that it exists, that its "
  "details are right, and that the cited paper says what the citing sentence claims. Seven "
  "members and three toolkeepers, which read the paper and look references up in public "
  "catalogues. Copy it into a team called <code>refs</code>, and give it a paper of your own, as "
  "a link or a PDF:")
with via("browser"):
    p(ui("New team") + ", <code>refs</code>, from <code>reference_check</code>. Then "
      + ui("Run…") + ", choose " + ui("A file") + " under " + ui("What to give the team")
      + ", and pick your PDF.")
with via("terminal"):
    run("teamrunner new refs --from reference_check", expect="refs")
    run("teamrunner explain refs", expect="toolkeeper")
    run("teamrunner run refs --file my_paper.pdf", skip=True)
p("Rehearsing it may end early: the reader's answer, whether it could read the whole paper, is "
  "random in a rehearsal, and the team stops when it can't. That is the flow working.")

parts.append('<h2 id="next">Where to go next</h2>')
ul(["<b>Start from the example closest to yours.</b> <a href=\"index.html#examples\">All six</a>, "
    "with what each adds.",
    f"<b>Read the reference.</b> Every file and every word a team may use is in the "
    f"<a href=\"{GH}#readme\">documentation</a>. Unsure of a word? See the "
    "<a href=\"index.html#glossary\">glossary</a>.",
    "<b>See what's coming,</b> and ask to hear when experiments arrive: "
    "<a href=\"index.html#coming\">what's coming</a>.",
    f"<b>Tell us what you found.</b> <a href=\"{GH}/issues/new/choose\">Open an issue</a>, or "
    "write to hello@teamrunner.ai."])

# --- the page --------------------------------------------------------------------------

# Browser first; a reader's choice is remembered, and tutorial.html#terminal opens the
# Terminal version (D137). Set before the page draws, so it never flickers. Without
# JavaScript both versions show.
CHOOSE = """<script>
(function(){var v='browser';try{v=localStorage.getItem('tr-via')||v}catch(e){}
if(location.hash==='#terminal'||location.hash==='#browser')v=location.hash.slice(1);
document.documentElement.setAttribute('data-via',v)})();
</script>
"""
SWITCH = """<script>
(function(){
  var root=document.documentElement;
  function mark(){var v=root.getAttribute('data-via');
    document.querySelectorAll('.via-switch button').forEach(function(b){
      b.setAttribute('aria-pressed',b.dataset.via===v?'true':'false')})}
  mark();
  document.querySelectorAll('.via-switch button').forEach(function(b){
    b.addEventListener('click',function(){
      var top=b.getBoundingClientRect().top;  // keep the clicked switch where it was
      root.setAttribute('data-via',b.dataset.via);
      try{localStorage.setItem('tr-via',b.dataset.via)}catch(e){}
      mark(); window.scrollBy(0,b.getBoundingClientRect().top-top);
    });
  });
})();
</script>
"""

home = pathlib.Path(out.parent, "index.html").read_text()
head = home[:home.index("<title>")]
mark = home[home.index("<svg"):home.index("</svg>") + len("</svg>")]
page = (head
        + "<title>Tutorial — TeamRunner</title>\n"
        + '<meta name="description" content="Nine steps on the teams that ship with TeamRunner, '
          'in your browser or in a terminal: a free rehearsal, a first real run, rounds, '
          'decisions, tools, private information and a first experiment. No code.">\n'
        + '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
        + '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        + '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        + home[home.index('<link rel="stylesheet" href="https://fonts'):home.index('<link rel="stylesheet" href="site.css">')]
        + '<link rel="stylesheet" href="site.css">\n'
        + CHOOSE
        + '</head>\n<body>\n'
        + f'''<header class="top">
  <div class="wrap">
    <a class="mark" href="index.html" aria-label="TeamRunner home">
      {mark}
      teamrunner
    </a>
    <nav aria-label="Main">
      <a href="index.html#why">Why</a>
      <a href="install.html">Install</a>
      <a href="tutorial.html" aria-current="page" style="color:var(--ink)">Tutorial</a>
      <a href="index.html#examples">Example</a>
      <a href="index.html#coming">What’s coming</a>
      <a href="index.html#reference">Reference</a>
    </nav>
    <div class="right">
      <span class="pill">preview</span>
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
'''
        + SWITCH
        + '''</body>
</html>
''')
out.write_text(page)
print("wrote", out, len(page), "bytes")
