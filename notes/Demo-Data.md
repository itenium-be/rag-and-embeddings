# Demo data — consultant data from BambooHR

The session runs on one dataset all the way through. BambooHR is a good choice: everyone in
the room is *in* it, so nobody has to be convinced the questions matter.

## The catch that makes it work

BambooHR is mostly **structured** — records and fields, not prose. That is the wrong shape
for naive RAG, and it is exactly the point of the session.

If you chunk a BambooHR export and embed it, you get a pile of near-identical text blobs
("Name: … Title: … Department: …") that all sit on top of each other in vector space, and
retrieval becomes a coin flip. That failure is the most honest possible demonstration of the
session's thesis: **retrieval over chunks is not a substitute for structure.**

So you need both halves:

| Source | Shape | Feeds |
| --- | --- | --- |
| BambooHR fields — title, department, manager, location, hire date, employment status, time off, training records, custom fields | Structured | The graph / text2cypher half. Counting, filtering, availability, org hierarchy |
| Consultant CVs and bios | Prose | The vector retrieval half. Experience, context, "who has done X" |
| Project / assignment one-pagers | Prose | Same, plus client and technology relationships |
| Skill self-assessments, training notes | Semi | Both. Good bridge material |
| The employee handbook / policies | Prose | The baseline question that works from the start |

The manager field is quietly the best thing in BambooHR for this session — it gives you a
**real org hierarchy for free**, which is a graph, which is a natural `MATCH` query, and
which no amount of chunk retrieval will ever answer.

itenium's own **SkillForge** data (skills, seniority levels, teams, validations, roadmaps)
is a second structured source worth pulling in — it is already modelled as entities and
relationships, so it drops straight into the graph half.

## Getting the data

BambooHR has a REST API: the employee directory, per-employee field selection, custom
reports, time off and training endpoints. A read-only API key and a nightly pull is enough —
nothing about this session needs to be live.

Pull once, commit the artefacts, and demo from those. See the pre-compute warning in the
[outline](Session-Outline.md).

## Before you export anything

This is real employee data in a real HR system, and embedding it is copying it: every chunk
you index lands in the vector store, and every chunk you retrieve goes to whichever LLM API
generates the answer. Whatever you embed, you have exported.

Worth being deliberate about, especially for a session that may be recorded or shared:

**Leave out.** Compensation, performance reviews and goals, home addresses, dates of birth,
national ID numbers, emergency contacts, and anything touching leave *reasons* (sick leave,
parental leave specifics) — that last category is health data and carries the heaviest
restrictions under GDPR.

**Keep.** Name, job title, department, manager, location, hire date, skills, certifications,
training completions, project history, availability. That is everything the five questions
actually need.

**Consider pseudonymizing.** If the session is recorded or shared beyond the room, swap real
names for consistent fake ones. The demo works identically and the recording stops being a
data export. The one thing to preserve is the *messiness* of the names — see question 4
below, which depends on the same person appearing three different ways.

There is also a purpose question worth thirty seconds of thought: HR data collected to
administer employment being repurposed for a search tool is a new purpose, and the people in
that data are the same people sitting in the room. Deciding this consciously before the
session is cheaper than deciding it afterwards.

**The upside**: this makes the access-control material (gap 7 in [Gaps](Gaps.md)) concrete
instead of theoretical. "Should a consultant be able to retrieve a chunk about a colleague's
performance?" is a much better slide when the answer is standing in front of you. Consider
making per-user filtering a *demoed feature* rather than a caveat — it is the most
production-relevant thing in the whole session and almost nobody covers it.

## The safest setup

Build the demo on a **pseudonymized snapshot** with the sensitive fields never exported, and
keep "wire it to the live BambooHR API with per-user access control" as the closing slide —
the thing you would do next, described rather than done. You lose nothing from the
demonstration and the whole question goes away.
