#!/usr/bin/env python3

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Extract the fixed ten-image MLPerf Tiny VWW sample set.

The source is an explicit directory containing ``non_person/`` and
``person/`` subdirectories.  The first five JPEGs in each directory, using
Unicode code-point lexical order, are copied byte-for-byte to the requested
output directory and described by the application manifest schema.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from PIL import Image


CLASS_ORDER = (("non_person", 0), ("person", 1))
SAMPLE_COUNT = 5
EXPECTED_SIZE = (96, 96)


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_dataset_root(dataset_root):
    dataset_root = Path(dataset_root)
    if not dataset_root.is_dir():
        raise ValueError(f"dataset root is not a directory: {dataset_root}")
    selected = []
    for class_name, label in CLASS_ORDER:
        class_dir = dataset_root / class_name
        if not class_dir.is_dir():
            raise ValueError(f"dataset is missing class directory: {class_dir}")
        candidates = sorted(
            path
            for path in class_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg"}
        )
        if len(candidates) < SAMPLE_COUNT:
            raise ValueError(
                f"dataset class {class_name!r} contains only {len(candidates)} JPEG files; "
                f"at least {SAMPLE_COUNT} are required"
            )
        for path in candidates[:SAMPLE_COUNT]:
            try:
                with Image.open(path) as image:
                    image.load()
                    if image.format != "JPEG" or image.size != EXPECTED_SIZE or image.mode != "RGB":
                        raise ValueError(
                            f"source image must be an RGB {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]} JPEG: {path}"
                        )
            except ValueError:
                raise
            except Exception as error:
                raise ValueError(f"source image is not a readable JPEG: {path}") from error
            selected.append((path, class_name, label))
    return tuple(selected)


def _validate_output_dir(output_dir, dataset_root):
    output_dir = Path(output_dir)
    if output_dir.is_symlink():
        raise ValueError(f"output path must not be a symbolic link: {output_dir}")
    try:
        output_resolved = output_dir.resolve()
        dataset_resolved = Path(dataset_root).resolve()
    except OSError as error:
        raise ValueError("could not resolve dataset or output path") from error
    if output_resolved == dataset_resolved or dataset_resolved in output_resolved.parents:
        raise ValueError("output directory must not be the dataset root or a child of it")
    if ".envs" in output_resolved.parts:
        raise ValueError("output directory must not be inside .envs")
    if output_resolved.exists() and not output_resolved.is_dir():
        raise ValueError(f"output path is not a directory: {output_dir}")
    return output_resolved


def _manifest_sample(source, class_name, label, filename):
    return {
        "filename": filename,
        "source_relative_path": f"{class_name}/{source.name}",
        "class_name": class_name,
        "label": label,
        "sha256": _sha256(source),
    }


def _validate_output_entry(path):
    """Reject destinations that are not safe final output entries."""
    try:
        path.lstat()
    except FileNotFoundError:
        return
    if path.is_symlink():
        raise ValueError(f"output destination must not be a symbolic link: {path}")
    if not path.is_file():
        raise ValueError(f"output destination must be a regular file: {path}")


def _atomic_write(path, payload):
    """Publish bytes without following or overwriting a non-regular target."""
    _validate_output_entry(path)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def extract_samples(dataset_root, output_dir):
    """Copy and describe the deterministic VWW sample selection."""
    dataset_root = Path(dataset_root)
    selected = _validate_dataset_root(dataset_root)
    output_dir = _validate_output_dir(output_dir, dataset_root)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_samples = []
    output_payloads = []
    for index, (source, class_name, label) in enumerate(selected):
        source_id = source.stem.rsplit("_", 1)[-1]
        filename = f"{index:02d}-{class_name.replace('_', '-')}-{source_id}.jpg"
        destination = output_dir / filename
        output_payloads.append((destination, source.read_bytes()))
        manifest_samples.append(_manifest_sample(source, class_name, label, filename))

    manifest = {
        "schema_version": 1,
        "dataset": {
            "name": "Visual Wake Words COCO 2014-derived dataset",
            "root": dataset_root.name,
            "source": "user-provided local dataset directory",
            "license": {
                "status": "not-declared-by-source",
                "notice": "The local COCO-derived image dataset license was not established by the source directory.",
            },
        },
        "selection": "lexicographically first five JPEG files from each class directory",
        "class_mapping": {"0": "non_person", "1": "person"},
        "samples": manifest_samples,
    }
    manifest_path = output_dir / "manifest.json"
    output_payloads.append(
        (manifest_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
    )
    for destination, _ in output_payloads:
        _validate_output_entry(destination)
    for destination, payload in output_payloads:
        _atomic_write(destination, payload)
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest_path = extract_samples(args.dataset_root, args.output_dir)
    print(f"Wrote deterministic VWW assets and manifest to {manifest_path.parent}")


if __name__ == "__main__":
    main()
