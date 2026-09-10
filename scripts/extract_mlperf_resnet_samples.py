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

"""Extract the fixed MLPerf ResNet sample set from an official CIFAR-10 test batch."""

import argparse
import binascii
import hashlib
import json
import pickle
import struct
import zlib
from pathlib import Path

import numpy as np


TEST_BATCH_SHA256 = "f53d8d457504f7cff4ea9e021afcf0e0ad8e24a91f3fc42091b8adef61157831"
CLASS_NAMES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _png_chunk(kind, payload):
    checksum = binascii.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)


def _encode_rgb_png(pixels):
    if pixels.dtype != np.uint8 or pixels.shape != (32, 32, 3):
        raise ValueError(f"expected uint8 RGB [32,32,3], got {pixels.dtype} {pixels.shape}")

    scanlines = b"".join(b"\x00" + pixels[row].tobytes() for row in range(32))
    header = struct.pack(">IIBBBBB", 32, 32, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", header)
        + _png_chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + _png_chunk(b"IEND", b"")
    )


def _load_verified_batch(test_batch_path):
    contents = test_batch_path.read_bytes()
    actual_sha256 = _sha256_bytes(contents)
    if actual_sha256 != TEST_BATCH_SHA256:
        raise ValueError(
            f"unexpected CIFAR-10 test_batch SHA-256 for {test_batch_path}: "
            f"expected {TEST_BATCH_SHA256}, got {actual_sha256}"
        )

    # Pickle is safe here only because the exact official bytes were authenticated above.
    batch = pickle.loads(contents, encoding="bytes")
    required_keys = {b"batch_label", b"labels", b"data", b"filenames"}
    if set(batch) != required_keys:
        raise ValueError(f"unexpected CIFAR-10 test_batch keys: {sorted(batch)}")
    if np.asarray(batch[b"data"]).shape != (10000, 3072):
        raise ValueError(f"unexpected CIFAR-10 test_batch data shape: {batch[b'data'].shape}")
    if len(batch[b"labels"]) != 10000 or len(batch[b"filenames"]) != 10000:
        raise ValueError("unexpected CIFAR-10 test_batch label or filename count")
    return batch


def _first_sample_per_class(batch):
    samples = {}
    for index, numeric_label in enumerate(batch[b"labels"]):
        numeric_label = int(numeric_label)
        if numeric_label not in range(10):
            raise ValueError(f"unexpected CIFAR-10 label {numeric_label} at test index {index}")
        if numeric_label in samples:
            continue

        chw = np.asarray(batch[b"data"][index], dtype="uint8").reshape(3, 32, 32)
        pixels = np.transpose(chw, (1, 2, 0)).copy()
        original_filename = batch[b"filenames"][index].decode("utf-8")
        samples[numeric_label] = (index, original_filename, pixels)
        if len(samples) == 10:
            break

    if set(samples) != set(range(10)):
        raise ValueError(f"test_batch does not contain every CIFAR-10 class: {sorted(samples)}")
    return samples


def _dataset_metadata():
    return {
        "name": "CIFAR-10",
        "version": "Python archive",
        "source_url": "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
        "archive": {
            "filename": "cifar-10-python.tar.gz",
            "md5": "c58f30108f718f92721af3b95e74349a",
        },
        "test_batch_sha256": TEST_BATCH_SHA256,
        "attribution": "Alex Krizhevsky, Vinod Nair, and Geoffrey Hinton",
        "citation": (
            "Alex Krizhevsky. Learning Multiple Layers of Features from Tiny Images. "
            "Technical report, 2009."
        ),
        "citation_url": "https://www.cs.toronto.edu/~kriz/learning-features-2009-TR.pdf",
        "license": {
            "status": "not-declared-by-source",
            "notice": (
                "The official CIFAR-10 distribution page does not declare an open-source license."
            ),
            "source_url": "https://www.cs.toronto.edu/~kriz/cifar.html",
        },
    }


def extract_samples(test_batch_path, output_dir):
    batch = _load_verified_batch(test_batch_path)
    selected = _first_sample_per_class(batch)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_samples = []
    for numeric_label in range(10):
        index, original_filename, pixels = selected[numeric_label]
        filename = f"{numeric_label:02d}-{CLASS_NAMES[numeric_label]}.png"
        png = _encode_rgb_png(pixels)
        (output_dir / filename).write_bytes(png)
        manifest_samples.append(
            {
                "filename": filename,
                "test_index": index,
                "numeric_label": numeric_label,
                "class_name": CLASS_NAMES[numeric_label],
                "original_filename": original_filename,
                "png_sha256": _sha256_bytes(png),
                "raw_rgb_sha256": _sha256_bytes(pixels.tobytes()),
            }
        )

    manifest = {
        "schema_version": 1,
        "dataset": _dataset_metadata(),
        "selection": "first test_batch occurrence of numeric labels 0 through 9",
        "samples": manifest_samples,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-batch", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest_path = extract_samples(args.test_batch, args.output_dir)
    print(f"Wrote deterministic CIFAR-10 assets and manifest to {manifest_path.parent}")


if __name__ == "__main__":
    main()
