"""Automated curricula integrity test suite for Milestone 2.

Verifies:
1. All 4 domains exist with valid READMEs and learnings directories.
2. All 11 priority topics exist and contain all 5 required canonical artifacts.
3. Every references.yaml contains citable literature conforming to schema with valid URLs and metadata.
4. Every rubric.md covers all 5 scoring dimensions across L4, L5, and L6.
5. Every exercises directory contains tier1_starter.md, tier2_l4.md, tier3_l5.md, and tier4_l6.md.
6. All root topic aliases and symlinks resolve to valid topic directories.
"""

import os
from pathlib import Path
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DOMAINS = [
    "leetcode",
    "system-design",
    "security",
    "privacy-engineering",
]

PRIORITY_TOPICS = {
    "leetcode": ["pythonic-patterns", "algorithms", "data-structures"],
    "system-design": ["statistics", "rust", "go"],
    "security": ["authn-authz", "threat-modeling", "agent-access-models"],
    "privacy-engineering": ["pets-for-ai", "differential-privacy"],
}

SCORING_DIMENSIONS = [
    "Problem Decomposition & Invariant Formulation",
    "Technical Execution & Code Craftsmanship",
    "Systems Architecture & Trade-Off Rigor",
    "Resilience, Security & Edge Case Posture",
    "Communication & Calibration Level",
]

TARGET_COMPANIES = [
    "OpenAI",
    "Google",
    "Anthropic",
    "Meta",
    "Databricks",
    "Netflix",
    "Apple",
]

ROOT_TOPIC_ALIASES = [
    "pythonic-coding-patterns",
    "masters-level-algorithms",
    "data-structures",
    "modern-authn-authz",
    "pets-for-ai",
    "threat-modeling",
    "access-models-for-agents",
    "statistics-for-data-analysis",
    "rust",
    "go",
    "modern-differential-privacy",
]


@pytest.mark.unit
def test_all_four_domains_exist_with_valid_readmes():
    """Verify all 4 domain root directories exist with non-empty READMEs and learnings."""
    for domain in DOMAINS:
        domain_dir = REPO_ROOT / domain
        assert domain_dir.is_dir(), f"Domain directory {domain} does not exist"

        readme_file = domain_dir / "README.md"
        assert readme_file.is_file(), f"Domain {domain} missing README.md"
        readme_text = readme_file.read_text(encoding="utf-8")
        assert len(readme_text) > 200, f"Domain {domain} README.md is suspiciously short ({len(readme_text)} bytes)"
        assert f"Domain: " in readme_text, f"Domain {domain} README.md missing Domain header"

        learnings_dir = domain_dir / "learnings"
        assert learnings_dir.is_dir(), f"Domain {domain} missing learnings directory"
        assert (learnings_dir / ".gitkeep").exists(), f"Domain {domain}/learnings missing .gitkeep"


@pytest.mark.unit
def test_all_eleven_priority_topics_exist_with_five_artifacts():
    """Verify all 11 priority topics exist under their canonical domains with required artifacts."""
    total_topics = 0
    for domain, topics in PRIORITY_TOPICS.items():
        for topic in topics:
            total_topics += 1
            topic_dir = REPO_ROOT / domain / topic
            assert topic_dir.is_dir(), f"Topic directory {domain}/{topic} does not exist"

            # 1. README.md
            readme_file = topic_dir / "README.md"
            assert readme_file.is_file(), f"Topic {domain}/{topic} missing README.md"
            readme_content = readme_file.read_text(encoding="utf-8")
            assert len(readme_content) > 300, f"Topic {domain}/{topic} README is too short"
            for company in TARGET_COMPANIES:
                assert company in readme_content, f"Topic {domain}/{topic} README missing company calibration for {company}"

            # 2. fundamentals.md
            fund_file = topic_dir / "fundamentals.md"
            assert fund_file.is_file(), f"Topic {domain}/{topic} missing fundamentals.md"
            fund_content = fund_file.read_text(encoding="utf-8")
            assert "Axiomatic Core Invariants" in fund_content, f"Topic {domain}/{topic} fundamentals missing invariants"
            assert "Core Mental Models" in fund_content, f"Topic {domain}/{topic} fundamentals missing mental models"
            assert "Idiomatic Code Examples" in fund_content, f"Topic {domain}/{topic} fundamentals missing code examples"
            assert "Architectural Tradeoffs" in fund_content, f"Topic {domain}/{topic} fundamentals missing tradeoffs"
            assert "Common Failure Modes" in fund_content, f"Topic {domain}/{topic} fundamentals missing failure modes"

            # 3. references.yaml and references.md
            ref_yaml = topic_dir / "references.yaml"
            assert ref_yaml.is_file(), f"Topic {domain}/{topic} missing references.yaml"
            ref_md = topic_dir / "references.md"
            assert ref_md.is_file(), f"Topic {domain}/{topic} missing references.md"

            # 4. rubric.md
            rubric_file = topic_dir / "rubric.md"
            assert rubric_file.is_file(), f"Topic {domain}/{topic} missing rubric.md"

            # 5. exercises/
            ex_dir = topic_dir / "exercises"
            assert ex_dir.is_dir(), f"Topic {domain}/{topic} missing exercises directory"

            # 6. learnings/
            learn_dir = topic_dir / "learnings"
            assert learn_dir.is_dir(), f"Topic {domain}/{topic} missing learnings directory"
            assert (learn_dir / ".gitkeep").exists(), f"Topic {domain}/{topic}/learnings missing .gitkeep"
            assert (learn_dir / "TEMPLATE.md").is_file(), f"Topic {domain}/{topic}/learnings missing TEMPLATE.md"

    assert total_topics == 11, f"Expected 11 priority topics, found {total_topics}"


@pytest.mark.unit
def test_references_yaml_schema_validity():
    """Verify every references.yaml contains valid YAML conforming to schema with valid URLs and metadata."""
    for domain, topics in PRIORITY_TOPICS.items():
        for topic in topics:
            ref_yaml = REPO_ROOT / domain / topic / "references.yaml"
            with open(ref_yaml, "r", encoding="utf-8") as f:
                refs = yaml.safe_load(f)

            assert isinstance(refs, list), f"{domain}/{topic} references.yaml must be a YAML list"
            assert len(refs) >= 2, f"{domain}/{topic} references.yaml has fewer than 2 citations ({len(refs)})"

            for ref in refs:
                assert "id" in ref and isinstance(ref["id"], str) and ref["id"], f"Missing id in {domain}/{topic} ref"
                assert "title" in ref and isinstance(ref["title"], str) and ref["title"], f"Missing title in {domain}/{topic} ref"
                assert "authors" in ref and isinstance(ref["authors"], list) and len(ref["authors"]) > 0, f"Missing authors in {domain}/{topic} ref"
                assert "year" in ref and isinstance(ref["year"], int) and 1970 <= ref["year"] <= 2030, f"Invalid year in {domain}/{topic} ref"
                assert "type" in ref and ref["type"] in ["paper", "book", "rfc", "course", "tech_blog", "interview_loop"], f"Invalid type in {domain}/{topic} ref"
                assert "canonical_url" in ref and ref["canonical_url"].startswith("http"), f"Invalid canonical_url in {domain}/{topic} ref"
                assert "key_invariants" in ref and isinstance(ref["key_invariants"], list) and len(ref["key_invariants"]) > 0, f"Missing key_invariants in {domain}/{topic} ref"
                assert "role_relevance" in ref and isinstance(ref["role_relevance"], list) and len(ref["role_relevance"]) > 0, f"Missing role_relevance in {domain}/{topic} ref"

                # Check interview calibration structure if present
                if "interview_calibration" in ref:
                    calib = ref["interview_calibration"]
                    assert "company" in calib, f"Missing company in calibration for {ref['id']}"
                    assert calib.get("level") in ["L4", "L5", "L6"], f"Invalid level in calibration for {ref['id']}"
                    assert "round_type" in calib, f"Missing round_type in calibration for {ref['id']}"
                    assert "expected_signals" in calib and len(calib["expected_signals"]) > 0, f"Missing expected_signals in calibration for {ref['id']}"


@pytest.mark.unit
def test_rubrics_cover_all_dimensions_and_levels():
    """Verify every rubric.md covers all 5 scoring dimensions across L4, L5, and L6."""
    for domain, topics in PRIORITY_TOPICS.items():
        for topic in topics:
            rubric_file = REPO_ROOT / domain / topic / "rubric.md"
            content = rubric_file.read_text(encoding="utf-8")

            # Must cover all 3 seniority levels
            assert "L4 (Mid-Level)" in content or "L4" in content, f"{domain}/{topic} rubric missing L4"
            assert "L5 (Senior)" in content or "L5" in content, f"{domain}/{topic} rubric missing L5"
            assert "L6 (Staff" in content or "L6" in content, f"{domain}/{topic} rubric missing L6"

            # Must cover all 5 dimensions
            for dim in SCORING_DIMENSIONS:
                assert dim in content, f"{domain}/{topic} rubric missing dimension: '{dim}'"


@pytest.mark.unit
def test_exercises_contain_all_four_tiers():
    """Verify every topic's exercises directory contains tier1_starter.md, tier2_l4.md, tier3_l5.md, tier4_l6.md."""
    required_tiers = ["tier1_starter.md", "tier2_l4.md", "tier3_l5.md", "tier4_l6.md"]
    for domain, topics in PRIORITY_TOPICS.items():
        for topic in topics:
            ex_dir = REPO_ROOT / domain / topic / "exercises"
            for tier in required_tiers:
                tier_file = ex_dir / tier
                assert tier_file.is_file(), f"Topic {domain}/{topic} missing exercise {tier}"
                content = tier_file.read_text(encoding="utf-8")
                assert len(content) > 200, f"Topic {domain}/{topic} exercise {tier} is too short"
                assert "Problem Statement" in content, f"Topic {domain}/{topic} exercise {tier} missing problem statement"
                assert "Starter Code" in content, f"Topic {domain}/{topic} exercise {tier} missing starter code"
                assert "Verification Test Cases" in content, f"Topic {domain}/{topic} exercise {tier} missing test cases"


@pytest.mark.unit
def test_root_topic_aliases_and_symlinks_resolve():
    """Verify all root topic aliases resolve to valid topic directories containing fundamentals.md."""
    for alias in ROOT_TOPIC_ALIASES:
        alias_path = REPO_ROOT / alias
        assert alias_path.exists(), f"Root topic alias {alias} does not exist"
        assert alias_path.is_dir(), f"Root topic alias {alias} is not a directory or symlink to dir"

        # Invariant: fundamentals.md, references.yaml, rubric.md must be accessible via root alias
        assert (alias_path / "fundamentals.md").is_file(), f"Root alias {alias} cannot access fundamentals.md"
        assert (alias_path / "references.yaml").is_file(), f"Root alias {alias} cannot access references.yaml"
        assert (alias_path / "rubric.md").is_file(), f"Root alias {alias} cannot access rubric.md"
        assert (alias_path / "exercises" / "tier1_starter.md").is_file(), f"Root alias {alias} cannot access tier1_starter.md"
