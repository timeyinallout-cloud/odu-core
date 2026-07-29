# Decisions

Choices that were made deliberately and could reasonably have gone the other
way. Recorded so they can be revisited on purpose rather than drifted away from.

## Interface language is English

The site, the CLI and the documentation are in English, while the subject is a
Yorùbá tradition and the maintainer speaks Yorùbá. That is a default, not a
judgement, and it deserves naming.

**What has been done:** every Yorùbá string in the generated site now carries
`lang="yo"`, so screen readers pronounce it as Yorùbá rather than mangling it as
English, and search engines index it correctly. This is a genuine correctness
fix, not a gesture — tone marks in an unmarked `lang="en"` context are read as
noise.

**What has not:** the interface strings are not translated. Translating them
would mean generating Yorùbá text, and this project's rule is that Yorùbá in
the dataset is sourced or attested, never generated. Interface copy is a
different category from corpus data — but a *bad* translation of a heritage
project's own interface is worse than an honest English one.

**To resolve:** a speaker supplies the interface strings, and they are recorded
with attribution like any other contribution. The `lang` scaffolding is already
in place, so this becomes a content task rather than an engineering one.

## Seniority default is southwestern Yorùbá

Bascom found it predominant — 42 of 86 lists — but that is barely half, and 21
other rankings are recorded. The Ifẹ variant is carried in `alternativeOrders`.

The default had to be *something*; what matters is that the library indexes by
bit pattern, so changing the default reorders nothing and breaks nothing.

## The corpus stores citations, not verses

Not a licensing workaround — a position. Ẹsẹ Ifá is living practice, some of it
initiation-restricted. Reproduction needs consent from people, which is a
different question from copyright and is not solved by a licence.

## Attested names beat constructed ones, even when identical

For most compound figures Bascom's attested name matches the name this dataset
constructs by concatenation. Both are recorded anyway, because *"a source lists
the figure under this name"* is a stronger claim than *"we joined two words"*,
even when the strings are byte-identical.
