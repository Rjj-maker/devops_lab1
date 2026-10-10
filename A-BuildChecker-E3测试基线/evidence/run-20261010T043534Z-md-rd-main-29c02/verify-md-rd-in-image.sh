#!/bin/sh
set -u
EVIDENCE=/evidence
capture() {
    name="$1"
    shift
    "$@" >"$EVIDENCE/$name.stdout.log" 2>"$EVIDENCE/$name.stderr.log"
    rc=$?
    printf '%s\n' "$rc" >"$EVIDENCE/$name.exit-code.txt"
    return "$rc"
}

# DRAFT build and test commands on the source copied from the selected commit.
cd /workspace || exit 1
capture draft-clean make clean || exit 1
capture draft-build make || exit 1
test -x ./app || exit 1
capture draft-test ./app || exit 1
test "$(cat "$EVIDENCE/draft-test.stdout.log")" = "1" || exit 1

# MD behavior: config.h is read but undeclared, so incremental make keeps stale output.
md=$(mktemp -d /tmp/md-rd-md.XXXXXX) || exit 1
cp -a /workspace/. "$md/" || exit 1
cd "$md" || exit 1
capture md-clean make clean || exit 1
capture md-build make || exit 1
capture md-initial-test ./app || exit 1
test "$(cat "$EVIDENCE/md-initial-test.stdout.log")" = "1" || exit 1
sed -i 's/#define VALUE 1/#define VALUE 2/' config.h || exit 1
sleep 2
touch config.h || exit 1
capture md-incremental make || exit 1
capture md-incremental-test ./app || exit 1
test "$(cat "$EVIDENCE/md-incremental-test.stdout.log")" = "1" || exit 1
make -s clean >/dev/null 2>&1 || exit 1
make >/dev/null 2>&1 || exit 1
capture md-clean-test ./app || exit 1
test "$(cat "$EVIDENCE/md-clean-test.stdout.log")" = "2" || exit 1

# RD behavior: changing the declared-but-unused header still rebuilds main.o.
rd=$(mktemp -d /tmp/md-rd-rd.XXXXXX) || exit 1
cp -a /workspace/. "$rd/" || exit 1
cd "$rd" || exit 1
capture rd-clean make clean || exit 1
capture rd-build make || exit 1
sed -i 's/unused dependency/unused dependency changed/' unused.h || true
sleep 2
touch unused.h || exit 1
capture rd-incremental make || exit 1
if ! grep -Eq 'main\.c|-[cC].*-o main\.o' "$EVIDENCE/rd-incremental.stdout.log"; then exit 1; fi
capture rd-test ./app || exit 1
test "$(cat "$EVIDENCE/rd-test.stdout.log")" = "1" || exit 1
printf 'draft_test=PASS\nmd_stale_behavior=PASS\nmd_clean_rebuild=PASS\nrd_rebuild=PASS\n' >"$EVIDENCE/in-image-checks.txt"
