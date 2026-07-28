-- Odù knowledge base schema.
--
-- One rule shapes this file: nothing that asserts something about Ifá can be
-- stored without a source. `source_id` is NOT NULL on every content table, so
-- an unattributed verse is not "discouraged" — it fails to insert. A corpus
-- that cannot say where a line came from has no value to anyone, and a corpus
-- of living sacred material that cannot say so is worse than empty.
--
-- Content is keyed to `odu_byte` (0-255), the stable identifier from
-- odu-core. Seniority rank is deliberately not used as a key: it varies by
-- lineage, and a record keyed to it would silently point at a different figure
-- under a different tradition.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Provenance
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS source (
    id                   INTEGER PRIMARY KEY,
    kind                 TEXT NOT NULL CHECK (kind IN (
                             'book', 'article', 'thesis', 'manuscript',
                             'field-recording', 'oral-contribution', 'web')),
    title                TEXT NOT NULL,
    author               TEXT,
    year                 INTEGER,
    publisher            TEXT,
    isbn                 TEXT,
    url                  TEXT,

    -- What we are allowed to do with the text, not merely who wrote it.
    rights               TEXT NOT NULL CHECK (rights IN (
                             'public-domain', 'cc-by', 'cc-by-sa',
                             'all-rights-reserved', 'contributor-licensed',
                             'unknown')),

    -- Whether the *text itself* may be republished. A source can be freely
    -- citable while its translations stay under copyright — Bascom (1969) and
    -- Abimbola (1976) are both in this position. Defaults to no.
    reproduction_allowed INTEGER NOT NULL DEFAULT 0 CHECK (reproduction_allowed IN (0, 1)),

    notes                TEXT,
    added_on             TEXT NOT NULL DEFAULT (date('now'))
);

-- People. Consent is tracked per person and can be withdrawn, which must
-- propagate to everything they contributed (see the publishable views below).
CREATE TABLE IF NOT EXISTS contributor (
    id                  INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    role                TEXT CHECK (role IN (
                            'babalawo', 'iyanifa', 'scholar', 'translator',
                            'transcriber', 'reciter', 'editor', NULL)),
    affiliation         TEXT,
    region              TEXT,
    lineage             TEXT,

    consent_status      TEXT NOT NULL CHECK (consent_status IN (
                            'granted', 'pending', 'withdrawn')),
    consent_recorded_on TEXT,
    consent_terms       TEXT,
    contact             TEXT,
    notes               TEXT
);

-- ---------------------------------------------------------------------------
-- Content
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS verse (
    id             INTEGER PRIMARY KEY,
    odu_byte       INTEGER NOT NULL CHECK (odu_byte BETWEEN 0 AND 255),

    source_id      INTEGER NOT NULL REFERENCES source(id) ON DELETE RESTRICT,
    contributor_id INTEGER REFERENCES contributor(id) ON DELETE RESTRICT,

    -- Nullable on purpose: a record may hold only a citation ("Bascom 1969,
    -- p. 314") when the text itself cannot be reproduced. A pointer to where
    -- a verse lives is still a real contribution.
    yoruba_text    TEXT,
    page_reference TEXT,
    sequence       INTEGER,

    -- Some ẹsẹ Ifá are initiation-restricted. Flagged material stays in the
    -- database for scholarship but never reaches a published view.
    restricted     INTEGER NOT NULL DEFAULT 0 CHECK (restricted IN (0, 1)),

    status         TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
                       'draft', 'review', 'published', 'withdrawn')),
    added_on       TEXT NOT NULL DEFAULT (date('now')),
    notes          TEXT,

    -- A record with neither text nor a page reference asserts nothing.
    CHECK (yoruba_text IS NOT NULL OR page_reference IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS translation (
    id         INTEGER PRIMARY KEY,
    verse_id   INTEGER NOT NULL REFERENCES verse(id) ON DELETE CASCADE,
    language   TEXT NOT NULL,          -- BCP-47, e.g. 'en', 'pt-BR'
    text       TEXT NOT NULL,
    translator TEXT,
    source_id  INTEGER NOT NULL REFERENCES source(id) ON DELETE RESTRICT,
    status     TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
                   'draft', 'review', 'published', 'withdrawn')),
    notes      TEXT,
    UNIQUE (verse_id, language, translator)
);

CREATE TABLE IF NOT EXISTS recording (
    id               INTEGER PRIMARY KEY,
    verse_id         INTEGER REFERENCES verse(id) ON DELETE CASCADE,
    odu_byte         INTEGER CHECK (odu_byte BETWEEN 0 AND 255),
    path             TEXT NOT NULL,
    duration_seconds REAL CHECK (duration_seconds IS NULL OR duration_seconds > 0),
    reciter_id       INTEGER REFERENCES contributor(id) ON DELETE RESTRICT,
    recorded_on      TEXT,
    location         TEXT,
    source_id        INTEGER NOT NULL REFERENCES source(id) ON DELETE RESTRICT,
    restricted       INTEGER NOT NULL DEFAULT 0 CHECK (restricted IN (0, 1)),
    status           TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
                         'draft', 'review', 'published', 'withdrawn')),
    notes            TEXT,
    -- Must attach to a verse or to a figure; a recording of nothing is a file.
    CHECK (verse_id IS NOT NULL OR odu_byte IS NOT NULL)
);

-- Commentary on a figure as a whole: attested alternative names, regional
-- variants, general interpretation. Also requires a source.
CREATE TABLE IF NOT EXISTS odu_note (
    id        INTEGER PRIMARY KEY,
    odu_byte  INTEGER NOT NULL CHECK (odu_byte BETWEEN 0 AND 255),
    kind      TEXT NOT NULL CHECK (kind IN (
                  'alternative-name', 'commentary', 'etymology',
                  'regional-variant', 'taboo', 'association')),
    text      TEXT NOT NULL,
    language  TEXT NOT NULL DEFAULT 'yo',
    lineage   TEXT,
    region    TEXT,
    source_id INTEGER NOT NULL REFERENCES source(id) ON DELETE RESTRICT,
    status    TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
                  'draft', 'review', 'published', 'withdrawn')),
    added_on  TEXT NOT NULL DEFAULT (date('now'))
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_verse_odu        ON verse(odu_byte);
CREATE INDEX IF NOT EXISTS idx_verse_status     ON verse(status);
CREATE INDEX IF NOT EXISTS idx_translation_verse ON translation(verse_id);
CREATE INDEX IF NOT EXISTS idx_recording_odu    ON recording(odu_byte);
CREATE INDEX IF NOT EXISTS idx_odu_note_odu     ON odu_note(odu_byte);

-- ---------------------------------------------------------------------------
-- Publishable views
--
-- The site generator reads only these. Publication is therefore the default-
-- deny path: a record reaches the public site only if it is marked published,
-- is not restricted, its source permits reproduction, and every contributor
-- attached to it still consents. Forgetting any one of those hides the record
-- rather than exposing it.
-- ---------------------------------------------------------------------------

CREATE VIEW IF NOT EXISTS publishable_verse AS
SELECT v.*
FROM verse v
JOIN source s ON s.id = v.source_id
LEFT JOIN contributor c ON c.id = v.contributor_id
WHERE v.status = 'published'
  AND v.restricted = 0
  AND (v.yoruba_text IS NULL OR s.reproduction_allowed = 1)
  AND (c.id IS NULL OR c.consent_status = 'granted');

CREATE VIEW IF NOT EXISTS publishable_translation AS
SELECT t.*
FROM translation t
JOIN source s ON s.id = t.source_id
JOIN publishable_verse v ON v.id = t.verse_id
WHERE t.status = 'published'
  AND s.reproduction_allowed = 1;

CREATE VIEW IF NOT EXISTS publishable_recording AS
SELECT r.*
FROM recording r
JOIN source s ON s.id = r.source_id
LEFT JOIN contributor c ON c.id = r.reciter_id
WHERE r.status = 'published'
  AND r.restricted = 0
  AND s.reproduction_allowed = 1
  AND (c.id IS NULL OR c.consent_status = 'granted');

CREATE VIEW IF NOT EXISTS publishable_note AS
SELECT n.*
FROM odu_note n
JOIN source s ON s.id = n.source_id
WHERE n.status = 'published'
  AND s.reproduction_allowed = 1;
