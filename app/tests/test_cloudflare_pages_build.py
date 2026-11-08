"""Unit and integration tests for Cloudflare Pages build artifacts and static catalog generation."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_pages.py"

# Dynamically import build_pages module from scripts/build_pages.py
spec = importlib.util.spec_from_file_location("build_pages_mod", SCRIPT_PATH)
assert spec and spec.loader, f"Failed to load module spec from {SCRIPT_PATH}"
build_pages_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_pages_mod)
build_pages = build_pages_mod.build_pages


@pytest.mark.unit
def test_build_pages_generates_all_required_artifacts(tmp_path: Path):
    """Verify build_pages generates complete distribution tree in target directory."""
    out_dir = tmp_path / "dist"
    result_path = build_pages(out_dir=out_dir, repo_root=REPO_ROOT)
    assert result_path == out_dir
    assert out_dir.is_dir()

    # Core HTML/CSS/JS files
    index_html = out_dir / "index.html"
    styles_css = out_dir / "static" / "styles.css"
    app_js = out_dir / "static" / "app.js"
    assert index_html.is_file() and index_html.stat().st_size > 0
    assert styles_css.is_file() and styles_css.stat().st_size > 0
    assert app_js.is_file() and app_js.stat().st_size > 0

    # Cloudflare Pages specific files
    headers_file = out_dir / "_headers"
    favicon_svg = out_dir / "favicon.svg"
    robots_txt = out_dir / "robots.txt"
    catalog_json = out_dir / "static" / "catalog.json"
    assert headers_file.is_file() and headers_file.stat().st_size > 0
    assert favicon_svg.is_file() and favicon_svg.stat().st_size > 0
    assert robots_txt.is_file() and robots_txt.stat().st_size > 0
    assert catalog_json.is_file() and catalog_json.stat().st_size > 0


@pytest.mark.unit
def test_cloudflare_headers_and_security_rules(tmp_path: Path):
    """Verify public/_headers contains all required security directives."""
    out_dir = tmp_path / "dist"
    build_pages(out_dir=out_dir, repo_root=REPO_ROOT)

    headers_content = (out_dir / "_headers").read_text(encoding="utf-8")
    assert "Content-Security-Policy:" in headers_content
    assert "default-src 'self'" in headers_content
    assert "connect-src 'self' http://127.0.0.1:8795 ws://127.0.0.1:8795" in headers_content
    assert "https://*.ts.net:8795" in headers_content
    assert "X-Content-Type-Options: nosniff" in headers_content
    assert "X-Frame-Options: DENY" in headers_content
    assert "Referrer-Policy: no-referrer" in headers_content
    assert "Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()" in headers_content
    assert "Strict-Transport-Security: max-age=31536000; includeSubDomains" in headers_content


@pytest.mark.unit
def test_static_catalog_json_schema_and_contents(tmp_path: Path):
    """Verify catalog.json schema, domains, >=11 topics, and curriculum details."""
    out_dir = tmp_path / "dist"
    build_pages(out_dir=out_dir, repo_root=REPO_ROOT)

    catalog_path = out_dir / "static" / "catalog.json"
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)

    # Site and timestamp
    assert catalog["site"] == "https://learn.willmccarty.io"
    assert "generated_at" in catalog

    # All 4 canonical domains present
    expected_domains = {"leetcode", "system-design", "security", "privacy-engineering"}
    assert set(catalog["domains"]) == expected_domains

    # Topics count >= 11
    topics = catalog["topics"]
    assert len(topics) >= 11

    # Verify each topic summary entry
    topic_slugs = set()
    for t in topics:
        assert "slug" in t
        assert "topic_id" in t
        assert "domain" in t and t["domain"] in expected_domains
        assert "title" in t and len(t["title"]) > 0
        assert "description" in t and len(t["description"]) > 0
        assert "role_tracks" in t and isinstance(t["role_tracks"], list)
        assert t["difficulty_tiers"] == ["starter", "l4", "l5", "l6"]
        assert t["user_rating"] == 3.0
        assert t["pinned"] is False
        topic_slugs.add(t["slug"])

    # Verify topic details map
    details = catalog["topic_details"]
    assert len(details) >= 11

    # Ensure key curriculum artifacts exist for every topic
    for slug in topic_slugs:
        assert slug in details, f"Topic detail missing for '{slug}'"
        d = details[slug]
        assert d["slug"] == slug
        assert d["topic_id"] == slug
        assert d["domain"] in expected_domains
        assert "readme" in d
        assert "fundamentals" in d and len(d["fundamentals"]) > 0
        assert "rubric" in d and len(d["rubric"]) > 0
        assert "references" in d and isinstance(d["references"], list)
        assert "exercises" in d and len(d["exercises"]) >= 4
        assert "learnings" in d

        # Check exercises structure
        for ex in d["exercises"]:
            assert "exercise_id" in ex
            assert "filename" in ex
            assert "title" in ex
            assert "content" in ex and len(ex["content"]) > 0

    # Verify company bars cover all 7 target companies
    expected_companies = {"Google", "OpenAI", "Anthropic", "Meta", "Databricks", "Netflix", "Apple"}
    company_bars = catalog["company_bars"]
    assert expected_companies.issubset(set(company_bars.keys()))
    for comp in expected_companies:
        assert "focus" in company_bars[comp]
        assert "anti_patterns" in company_bars[comp]
        assert "weights" in company_bars[comp]
        assert round(sum(company_bars[comp]["weights"].values()), 2) == 1.00

    # Verify role tracks
    role_tracks = catalog["role_tracks"]
    assert "faang_swe_l5_l6" in role_tracks
    assert "faang_privacy_l6" in role_tracks
    assert "faang_security_l4_l6" in role_tracks
    assert "ai_lab_research_l4_l5" in role_tracks


@pytest.mark.unit
def test_build_pages_cli_invocation(tmp_path: Path):
    """Verify scripts/build_pages.py is directly executable via command line."""
    cli_out_dir = tmp_path / "cli_dist"
    cmd = [sys.executable, str(SCRIPT_PATH), "--out-dir", str(cli_out_dir)]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    assert res.returncode == 0, f"CLI build failed: {res.stderr}"
    assert (cli_out_dir / "index.html").is_file()
    assert (cli_out_dir / "static" / "catalog.json").is_file()


@pytest.mark.unit
def test_cloudflare_config_and_package_metadata():
    """Verify package.json, .nvmrc, and wrangler.toml configuration."""
    nvmrc_path = REPO_ROOT / ".nvmrc"
    assert nvmrc_path.is_file()
    assert nvmrc_path.read_text(encoding="utf-8").strip() == "22.23.4"

    pkg_path = REPO_ROOT / "package.json"
    assert pkg_path.is_file()
    with open(pkg_path, encoding="utf-8") as f:
        pkg = json.load(f)
    assert pkg["name"] == "learn.willmccarty.io"
    assert pkg["private"] is True
    assert "build" in pkg["scripts"]
    assert "preview" in pkg["scripts"]

    wrangler_path = REPO_ROOT / "wrangler.toml"
    assert wrangler_path.is_file()
    wrangler_content = wrangler_path.read_text(encoding="utf-8")
    assert 'name = "learn"' in wrangler_content
    assert 'pages_build_output_dir = "dist"' in wrangler_content


@pytest.mark.unit
def test_build_does_not_dirty_git(tmp_path: Path):
    """Verify building static distribution does not produce unignored git artifacts."""
    # Verify dist/ is in .gitignore
    gitignore_path = REPO_ROOT / ".gitignore"
    assert gitignore_path.is_file()
    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    assert "dist/" in gitignore_content
    assert "node_modules/" in gitignore_content

    # Check git status before
    status_before = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    # Run build to default repo_root / dist
    build_pages(repo_root=REPO_ROOT)

    # Check git status after - dist/ must be completely ignored
    status_after = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    # Any new untracked files must not include dist/
    diff_lines = [
        line for line in status_after.splitlines()
        if line not in status_before.splitlines()
    ]
    for line in diff_lines:
        assert not line.strip().endswith("dist/"), f"dist/ was not ignored by git: {line}"
        assert "dist/" not in line, f"dist/ contents were not ignored by git: {line}"
