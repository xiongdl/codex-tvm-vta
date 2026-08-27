#!/usr/bin/env sh
set -eu
source_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture_root=
cleanup() { if [ -n "$fixture_root" ]; then rm -rf "$fixture_root"; fi; }
trap cleanup EXIT HUP INT TERM
fail() { echo "FAIL: $*" >&2; exit 1; }
assert_success() { description=$1; shift; "$@" >/dev/null 2>&1 || fail "$description"; }
assert_failure() { description=$1; shift; if "$@" >/dev/null 2>&1; then fail "$description"; fi; }
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
  done
  printf '%s\n' '[submodule "tvm"]' '    path = tvm' '    url = https://github.com/xiongdl/tvm.git' '    branch = tvm_v0.17.0' '[submodule "vta"]' '    path = vta' '    url = https://github.com/xiongdl/vta.git' '    branch = vta_v0.0.2' >"$fixture_root/.gitmodules"
  git -C "$fixture_root" add --no-warn-embedded-repo README.md docs scripts .gitmodules tvm vta
  git -C "$fixture_root" commit -qm fixture
}
new_fixture; assert_success "valid fixture should verify" "$fixture_root/scripts/project" verify; assert_success "valid fixture status should run" "$fixture_root/scripts/project" status
new_fixture; : >"$fixture_root/dirty"; assert_failure "dirty workspace should fail" "$fixture_root/scripts/project" verify
new_fixture; : >"$fixture_root/tvm/dirty"; assert_failure "dirty submodule should fail" "$fixture_root/scripts/project" verify
new_fixture; : >"$fixture_root/tvm/next"; git -C "$fixture_root/tvm" add next; git -C "$fixture_root/tvm" commit -qm next; assert_failure "gitlink mismatch should fail" "$fixture_root/scripts/project" verify
new_fixture; git -C "$fixture_root" config -f .gitmodules submodule.tvm.url https://example.invalid/tvm.git; git -C "$fixture_root" add .gitmodules; git -C "$fixture_root" commit -qm wrong-config; assert_failure "wrong configuration should fail" "$fixture_root/scripts/project" verify
new_fixture; printf '%s\n' '[broken' >"$fixture_root/.gitmodules"; git -C "$fixture_root" add .gitmodules; git -C "$fixture_root" commit -qm malformed-config; assert_failure "malformed configuration should fail" "$fixture_root/scripts/project" verify
echo "PASS: project CLI tests"
