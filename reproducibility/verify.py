#!/usr/bin/env python3
"""Unified integrity and reproduction entry point for the manuscript."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


REPOSITORY = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
PAPER_SOURCE = REPOSITORY / "paper" / "manuscript.tex"
PAPER_PDF = REPOSITORY / "paper" / "manuscript.pdf"
ARCHIVE_MANIFEST = HERE / "archives.sha256"

EXPECTED_PAPER_HASHES = {
    PAPER_SOURCE: "67099079949f530090fe3bfc9ca5003f8e542a78933ab07218eb8701ec2cc932",
    PAPER_PDF: "611f81279008bc678bb71597da50356b1950a3dbb89eb301aa5328758a66444b",
}

FAST_COMMANDS = [
    [sys.executable, "manuscript_consistency_audit.py"],
    [
        sys.executable,
        "verify_quartic_bundle.py",
        "--catalog",
        "quartic_norm_sieve_exact.json",
        "--tail",
        "quartic_uniform_negative_exact.json",
        "--finite",
        "quartic_finite_recurrence_exact.json",
        "--prefix",
        "quartic_prefix_q1_exact.json",
        "--prefix",
        "quartic_prefix_q2_exact.json",
        "--prefix",
        "quartic_prefix_q3_exact.json",
        "--prefix",
        "quartic_prefix_q4_exact.json",
    ],
]

FULL_BASE_COMMANDS = [
    [
        sys.executable,
        "cubic_gap2_degree75_search.py",
        "--output",
        "cubic_gap2_degree75_results.json",
        "--certificate-output",
        "cubic_gap2_degree75_farkas.json",
    ],
    [sys.executable, "verify_uniform_cubic_catalog.py"],
    [sys.executable, "verify_forced_recurrence_global.py"],
    [sys.executable, "verify_block_positivity_global.py"],
    [sys.executable, "verify_parity_rationalization.py"],
    [sys.executable, "verify_predecessor_safe_lattice.py"],
    [sys.executable, "verify_predecessor_safe_lattice_monotonicity.py"],
    [sys.executable, "verify_predecessor_three_block.py"],
    [sys.executable, "verify_predecessor_three_block_signs.py"],
    [sys.executable, "verify_predecessor_four_block.py"],
    [sys.executable, "verify_predecessor_four_block_signs.py"],
    [sys.executable, "verify_predecessor_five_block.py"],
    [sys.executable, "verify_predecessor_five_block_signs.py"],
    [sys.executable, "verify_predecessor_six_block.py"],
    [sys.executable, "verify_predecessor_six_block_signs.py"],
    [
        sys.executable,
        "quartic_norm_sieve_exact.py",
        "--output",
        "quartic_norm_sieve_exact.json",
    ],
    [
        sys.executable,
        "quartic_uniform_negative_exact.py",
        "--catalog",
        "quartic_norm_sieve_exact.json",
        "--output",
        "quartic_uniform_negative_exact.json",
        "--max-k",
        "130",
        "--max-offset",
        "100",
    ],
    [
        sys.executable,
        "quartic_finite_recurrence_exact.py",
        "--catalog",
        "quartic_norm_sieve_exact.json",
        "--tail",
        "quartic_uniform_negative_exact.json",
        "--output",
        "quartic_finite_recurrence_exact.json",
    ],
]

QUARTERS = [
    ("q1", "1", "1746"),
    ("q2", "1747", "3491"),
    ("q3", "3492", "5237"),
    ("q4", "5238", "6982"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        if name in entries:
            raise ValueError(f"duplicate manifest entry: {name}")
        entries[name] = digest
    return entries


def verify_archive(path: Path, expected_hash: str) -> None:
    actual = sha256(path)
    if actual != expected_hash:
        raise RuntimeError(f"archive hash mismatch for {path.name}: {actual}")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "MANIFEST.sha256" not in names:
            raise RuntimeError(f"{path.name} has no MANIFEST.sha256")
        manifest = parse_manifest(
            archive.read("MANIFEST.sha256").decode("utf-8")
        )
        expected_names = set(manifest) | {"MANIFEST.sha256"}
        if names != expected_names:
            missing = sorted(expected_names - names)
            extra = sorted(names - expected_names)
            raise RuntimeError(
                f"{path.name} member mismatch; missing={missing}, extra={extra}"
            )
        for name, digest in manifest.items():
            actual_member = hashlib.sha256(archive.read(name)).hexdigest()
            if actual_member != digest:
                raise RuntimeError(
                    f"{path.name}:{name} hash mismatch: {actual_member}"
                )


def integrity() -> None:
    for path, expected in EXPECTED_PAPER_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"paper hash mismatch for {path}: {actual}")

    archives = parse_manifest(ARCHIVE_MANIFEST.read_text(encoding="utf-8"))
    expected_archive_names = {"source.zip", "certificates.zip"}
    if set(archives) != expected_archive_names:
        raise RuntimeError(
            f"archives.sha256 must contain {sorted(expected_archive_names)}"
        )
    for name, digest in archives.items():
        verify_archive(HERE / name, digest)

    print("Integrity verification passed.")


def safe_extract(archive_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination not in target.parents and target != destination:
                raise RuntimeError(
                    f"unsafe archive member in {archive_path.name}: "
                    f"{member.filename}"
                )
            archive.extract(member, destination)


def run(command: list[str], workdir: Path) -> None:
    print("> " + " ".join(command), flush=True)
    subprocess.run(command, cwd=workdir, check=True)


def prepare_workspace() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="newman-reproduction-")
    workspace = Path(temporary.name)
    safe_extract(HERE / "source.zip", workspace)
    safe_extract(HERE / "certificates.zip", workspace)
    shutil.copy2(
        PAPER_SOURCE,
        workspace / "manuscript.tex",
    )
    return temporary, workspace


def fast() -> None:
    temporary, workspace = prepare_workspace()
    try:
        for command in FAST_COMMANDS:
            run(command, workspace)
    finally:
        temporary.cleanup()
    print("Fast mathematical verification passed.")


def full_commands() -> list[list[str]]:
    commands = [*FULL_BASE_COMMANDS]
    for name, start, end in QUARTERS:
        commands.extend(
            [
                [
                    sys.executable,
                    "quartic_prefix_positivity_exact.py",
                    "--tail",
                    "quartic_uniform_negative_exact.json",
                    "--output",
                    f"quartic_prefix_{name}_exact.json",
                    "--start",
                    start,
                    "--end",
                    end,
                ],
                [
                    sys.executable,
                    "independent_finite_arb_audit.py",
                    "--start",
                    start,
                    "--end",
                    end,
                    "--output",
                    f"independent_finite_arb_{name}.json",
                ],
                [
                    sys.executable,
                    "independent_uniform_arb_audit.py",
                    "--start",
                    start,
                    "--end",
                    end,
                    "--output",
                    f"independent_uniform_arb_{name}.json",
                ],
                [
                    sys.executable,
                    "independent_uniform_direct_recurrence_stress.py",
                    "--start",
                    start,
                    "--end",
                    end,
                    "--v",
                    "23",
                    "--v",
                    "251",
                    "--output",
                    f"independent_uniform_direct_{name}.json",
                ],
            ]
        )
    commands.extend(
        [
            [sys.executable, "independent_quartic_catalog_audit.py"],
            [sys.executable, "merge_independent_quartic_audits.py"],
            [sys.executable, "merge_independent_uniform_direct_stress.py"],
            [sys.executable, "manuscript_consistency_audit.py"],
            [
                "tectonic",
                "-X",
                "compile",
                "manuscript.tex",
            ],
        ]
    )
    return commands


def full() -> None:
    temporary, workspace = prepare_workspace()
    try:
        for command in full_commands():
            run(command, workspace)
    finally:
        temporary.cleanup()
    print("Complete regeneration passed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--fast",
        action="store_true",
        help="run retained-certificate mathematical checks",
    )
    modes.add_argument(
        "--full",
        action="store_true",
        help="run the expensive complete regeneration",
    )
    args = parser.parse_args()

    integrity()
    if args.fast:
        fast()
    elif args.full:
        full()


if __name__ == "__main__":
    main()
