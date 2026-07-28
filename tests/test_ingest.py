"""Tests for the content-file ingest.

The ingest is the boundary between hand-written text and the database, so these
tests are mostly about malformed or disallowed content being *rejected with a
useful message* rather than quietly landing in the corpus.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location("ingest", ROOT / "scripts" / "ingest.py")
ingest = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(ingest)


@pytest.fixture
def content(tmp_path, monkeypatch):
    """A throwaway kb/content tree the tests can write files into."""
    root = tmp_path / "content"
    (root / "sources").mkdir(parents=True)
    (root / "contributors.json").write_text(
        json.dumps({"contributors": []}), encoding="utf-8"
    )
    monkeypatch.setattr(ingest, "CONTENT", root)
    return root


def write_source(content: Path, slug: str, **overrides):
    payload = {
        "source": {
            "slug": slug,
            "kind": "oral-contribution",
            "title": f"Source {slug}",
            "rights": "contributor-licensed",
        },
        "verses": [],
        "notes": [],
    }
    payload.update(overrides)
    (content / "sources" / f"{slug}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    return payload


def run(tmp_path):
    return ingest.run(tmp_path / "out.db")


class TestFigureResolution:
    @pytest.mark.parametrize(
        "ref,expected",
        [("ogbe-ogbe", 255), ("oyeku-oyeku", 0), (44, 44), ("44", 44),
         ("Òtúrúpọ̀n Ìrosùn", 44), ("oturupon-irosun", 44)],
    )
    def test_accepts_slugs_bytes_and_names(self, ref, expected):
        assert ingest.resolve_odu(ref) == expected

    @pytest.mark.parametrize("bad", ["nonsense", "ogbe", 999, -1, None, True, ["a"]])
    def test_rejects_anything_it_cannot_resolve(self, bad):
        with pytest.raises((ValueError, KeyError, TypeError)):
            ingest.resolve_odu(bad)

    def test_a_typo_does_not_silently_pick_a_figure(self):
        with pytest.raises((ValueError, KeyError)):
            ingest.resolve_odu("ogbe-oyekk")


class TestIngest:
    def test_clean_content_produces_no_problems(self, content, tmp_path):
        write_source(content, "clean")
        problems, summary = run(tmp_path)
        assert not problems, problems.items
        assert summary["sources"] == 1

    def test_missing_sources_directory_is_reported(self, content, tmp_path):
        for f in (content / "sources").glob("*.json"):
            f.unlink()
        problems, _ = run(tmp_path)
        assert any("no source files" in p for p in problems.items)

    def test_invalid_json_is_reported_not_raised(self, content, tmp_path):
        (content / "sources" / "broken.json").write_text("{not json", encoding="utf-8")
        problems, _ = run(tmp_path)
        assert any("invalid JSON" in p for p in problems.items)

    def test_file_without_a_source_block_is_rejected(self, content, tmp_path):
        (content / "sources" / "orphan.json").write_text(
            json.dumps({"verses": [{"odu": "ogbe-ogbe", "pageReference": "p. 1"}]}),
            encoding="utf-8",
        )
        problems, _ = run(tmp_path)
        assert any("must name its source" in p for p in problems.items)

    def test_verse_is_loaded_and_counted(self, content, tmp_path):
        write_source(content, "ok", verses=[
            {"odu": "ogbe-ogbe", "yorubaText": "…", "status": "published"}
        ])
        problems, summary = run(tmp_path)
        assert not problems, problems.items
        assert summary["verses"] == 1
        assert summary["figures_covered"] == 1

    def test_copyrighted_source_cannot_carry_text(self, content, tmp_path):
        write_source(
            content, "closed",
            source={"slug": "closed", "kind": "book", "title": "A Book",
                    "rights": "all-rights-reserved"},
            verses=[{"odu": "ogbe-ogbe", "yorubaText": "…"}],
        )
        problems, _ = run(tmp_path)
        assert any("cannot be stored" in p for p in problems.items)

    def test_copyrighted_source_may_carry_a_citation(self, content, tmp_path):
        write_source(
            content, "closed",
            source={"slug": "closed", "kind": "book", "title": "A Book",
                    "rights": "all-rights-reserved"},
            verses=[{"odu": "ogbe-ogbe", "pageReference": "p. 314"}],
        )
        problems, summary = run(tmp_path)
        assert not problems, problems.items
        assert summary["verses"] == 1

    def test_verse_with_neither_text_nor_citation_is_rejected(self, content, tmp_path):
        write_source(content, "empty", verses=[{"odu": "ogbe-ogbe"}])
        problems, _ = run(tmp_path)
        assert any("asserts nothing" in p for p in problems.items)

    def test_unknown_figure_reference_is_rejected(self, content, tmp_path):
        write_source(content, "bad", verses=[
            {"odu": "not-a-figure", "pageReference": "p. 1"}
        ])
        problems, _ = run(tmp_path)
        assert any("not a figure" in p or "no principal" in p for p in problems.items)

    def test_all_problems_surface_in_one_pass(self, content, tmp_path):
        write_source(content, "many", verses=[
            {"odu": "not-a-figure", "pageReference": "p. 1"},
            {"odu": "ogbe-ogbe"},
            {"odu": "also-not-real", "pageReference": "p. 2"},
        ])
        problems, _ = run(tmp_path)
        assert len(problems.items) >= 3, problems.items


class TestContributors:
    def test_unknown_contributor_reference_is_rejected(self, content, tmp_path):
        write_source(content, "s", verses=[
            {"odu": "ogbe-ogbe", "yorubaText": "…", "contributor": "ghost"}
        ])
        problems, _ = run(tmp_path)
        assert any("unknown contributor" in p for p in problems.items)

    def test_contributor_without_consent_status_is_rejected(self, content, tmp_path):
        (content / "contributors.json").write_text(
            json.dumps({"contributors": [{"slug": "a", "name": "A Person"}]}),
            encoding="utf-8",
        )
        write_source(content, "s")
        problems, _ = run(tmp_path)
        assert any("consentStatus is required" in p for p in problems.items)

    def test_consenting_contributor_links_through(self, content, tmp_path):
        (content / "contributors.json").write_text(
            json.dumps({"contributors": [
                {"slug": "a", "name": "A Person", "consentStatus": "granted"}
            ]}),
            encoding="utf-8",
        )
        write_source(content, "s", verses=[
            {"odu": "ogbe-ogbe", "yorubaText": "…", "contributor": "a",
             "status": "published"}
        ])
        problems, summary = run(tmp_path)
        assert not problems, problems.items
        assert summary["contributors"] == 1
        assert summary["verses_publishable"] == 1

    def test_withdrawn_consent_blocks_publication_through_ingest(self, content, tmp_path):
        (content / "contributors.json").write_text(
            json.dumps({"contributors": [
                {"slug": "a", "name": "A Person", "consentStatus": "withdrawn"}
            ]}),
            encoding="utf-8",
        )
        write_source(content, "s", verses=[
            {"odu": "ogbe-ogbe", "yorubaText": "…", "contributor": "a",
             "status": "published"}
        ])
        problems, summary = run(tmp_path)
        assert not problems, problems.items
        assert summary["verses"] == 1
        assert summary["verses_publishable"] == 0


class TestRebuildIsClean:
    def test_rebuilding_does_not_accumulate_duplicates(self, content, tmp_path):
        write_source(content, "s", verses=[
            {"odu": "ogbe-ogbe", "yorubaText": "…"}
        ])
        first = run(tmp_path)[1]
        second = run(tmp_path)[1]
        assert first["verses"] == second["verses"] == 1
        assert first["sources"] == second["sources"] == 1

    def test_removing_a_file_removes_its_content(self, content, tmp_path):
        write_source(content, "s", verses=[{"odu": "ogbe-ogbe", "yorubaText": "…"}])
        assert run(tmp_path)[1]["verses"] == 1
        (content / "sources" / "s.json").unlink()
        assert run(tmp_path)[1]["verses"] == 0
