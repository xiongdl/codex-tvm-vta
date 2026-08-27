#!/usr/bin/env sh
set -eu
source_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture_root=
cleanup() { if [ -n "$fixture_root" ]; then rm -rf "$fixture_root"; fi; }
trap cleanup EXIT HUP INT TERM
fail() { echo "FAIL: $*" >&2; exit 1; }
assert_success() { description=$1; shift; "$@" >/dev/null 2>&1 || fail "$description"; }
assert_exit() {
  expected=$1; description=$2; shift 2
  set +e
  "$@" >/dev/null 2>&1
  actual=$?
  set -e
  if [ "$actual" -ne "$expected" ]; then fail "$description (expected $expected, got $actual)"; fi
}
new_fixture() {
  cleanup
  fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/project-cli-test.XXXXXX")
  mkdir -p "$fixture_root/scripts" "$fixture_root/docs"
  cp "$source_root/scripts/project" "$fixture_root/scripts/project"; chmod +x "$fixture_root/scripts/project"
  for file in ARCHITECTURE.md PROJECT_STATUS.md REPRODUCIBILITY.md; do : >"$fixture_root/docs/$file"; done
  : >"$fixture_root/README.md"
  git -C "$fixture_root" init -q; git -C "$fixture_root" config user.name Test; git -C "$fixture_root" config user.email test@example.invalid
  git -C "$fixture_root" config advice.addEmbeddedRepo false
  for name in tvm vta; do
    mkdir "$fixture_root/$name"; git -C "$fixture_root/$name" init -q
    git -C "$fixture_root/$name" config user.name Test; git -C "$fixture_root/$name" config user.email test@example.invalid
    : >"$fixture_root/$name/source"; git -C "$fixture_root/$name" add source; git -C "$fixture_root/$name" commit -qm baseline
    if [ "$name" = tvm ]; then git -C "$fixture_root/$name" branch -m tvm_v0.17.0; else git -C "$fixture_root/$name" branch -m vta_v0.0.2; fi
  done
  printf '%s\n' '[submodule "tvm"]' '    path = tvm' '    url = https://github.com/xiongdl/tvm.git' '    branch = tvm_v0.17.0' '[submodule "vta"]' '    path = vta' '    url = https://github.com/xiongdl/vta.git' '    branch = vta_v0.0.2' >"$fixture_root/.gitmodules"
  git -C "$fixture_root" add --no-warn-embedded-repo README.md docs scripts .gitmodules tvm vta
  git -C "$fixture_root" commit -qm fixture
}
new_fixture; assert_exit 0 "valid fixture verify" "$fixture_root/scripts/project" verify; assert_exit 0 "READY status" "$fixture_root/scripts/project" status
new_fixture; git -C "$fixture_root/tvm" branch -m task/test; assert_exit 0 "warning-only status" "$fixture_root/scripts/project" status
new_fixture; : >"$fixture_root/dirty"; assert_exit 1 "dirty workspace verify" "$fixture_root/scripts/project" verify; assert_exit 1 "NOT_READY status" "$fixture_root/scripts/project" status
new_fixture; : >"$fixture_root/tvm/dirty"; assert_exit 1 "dirty submodule verify" "$fixture_root/scripts/project" verify
new_fixture; : >"$fixture_root/tvm/next"; git -C "$fixture_root/tvm" add next; git -C "$fixture_root/tvm" commit -qm next; assert_exit 1 "gitlink mismatch verify" "$fixture_root/scripts/project" verify
new_fixture; git -C "$fixture_root" config -f .gitmodules submodule.tvm.url https://example.invalid/tvm.git; git -C "$fixture_root" add .gitmodules; git -C "$fixture_root" commit -qm wrong-config; assert_exit 1 "wrong configuration verify" "$fixture_root/scripts/project" verify
new_fixture; printf '%s\n' '[broken' >"$fixture_root/.gitmodules"; git -C "$fixture_root" add .gitmodules; git -C "$fixture_root" commit -qm malformed-config; assert_exit 1 "malformed configuration verify" "$fixture_root/scripts/project" verify
cleanup; fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/project-cli-test.XXXXXX"); mkdir -p "$fixture_root/scripts"; cp "$source_root/scripts/project" "$fixture_root/scripts/project"
assert_exit 2 "unconfigured status" "$fixture_root/scripts/project" status; assert_exit 2 "unconfigured verify" "$fixture_root/scripts/project" verify
echo "PASS: project CLI tests"
