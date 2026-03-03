#!/usr/bin/env bash
# push-github.sh — Sync text-only paths to github.com, skipping LFS blobs.
#
# Strategy: create a temporary git worktree rooted at github/main, overlay the
# current state of all non-LFS paths from main, commit, and force-push to
# github/main.  Using a worktree keeps the main working tree completely
# undisturbed (no branch switching, no untracked-file conflicts).
#
# Paths included in the github sync are listed in SYNC_PATHS below.
#
# Usage:  bash automation/push-github.sh [--dry-run]
set -euo pipefail

REMOTE="github"
REMOTE_BRANCH="main"
DRY_RUN=0

# Paths to sync to github (non-LFS content)
SYNC_PATHS=(
    automation/
    .gitattributes
    .gitignore
)

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "=== DRY RUN ==="
fi

cd "$(git rev-parse --show-toplevel)"

# Fetch latest github state
echo "Fetching $REMOTE/$REMOTE_BRANCH..."
git fetch "$REMOTE" "$REMOTE_BRANCH" 2>/dev/null || true

GITHUB_HEAD=$(git rev-parse "$REMOTE/$REMOTE_BRANCH" 2>/dev/null || echo "")

if [[ -z "$GITHUB_HEAD" ]]; then
    echo "ERROR: Could not resolve $REMOTE/$REMOTE_BRANCH"
    exit 1
fi

# Show what automation commits are pending
PENDING_COUNT=$(git log --oneline "$GITHUB_HEAD..main" -- "${SYNC_PATHS[@]}" | wc -l | tr -d ' ')
echo ""
echo "Automation commits since last github push: $PENDING_COUNT"
git log --oneline "$GITHUB_HEAD..main" -- "${SYNC_PATHS[@]}"
echo ""

if [[ "$PENDING_COUNT" -eq 0 ]]; then
    echo "Nothing to push."
    exit 0
fi

# Use a temporary worktree rooted at github/main.  This is completely isolated
# from the main working tree, so untracked files / staged changes there never
# interfere with the branch operations here.
TMP_WORKTREE=$(mktemp -d)
cleanup() {
    git worktree remove --force "$TMP_WORKTREE" 2>/dev/null || true
    rm -rf "$TMP_WORKTREE"
}
trap cleanup EXIT

echo "Building sync commit in temporary worktree..."
# GIT_LFS_SKIP_SMUDGE=1 so we don't try to download LFS blobs for github/main
GIT_LFS_SKIP_SMUDGE=1 git worktree add -q --detach "$TMP_WORKTREE" "$GITHUB_HEAD"

# Overlay current state of sync paths from main into the worktree index
git -C "$TMP_WORKTREE" checkout main -- "${SYNC_PATHS[@]}" 2>/dev/null || true

# Check if anything actually changed relative to github/main
if git -C "$TMP_WORKTREE" diff --cached --quiet; then
    echo "No changes in sync paths — nothing to push."
    exit 0
fi

# Build a commit message summarising what changed
MSG="Sync from main@$(git rev-parse --short main)

Automation commits included:
$(git log --oneline "$GITHUB_HEAD..main" -- "${SYNC_PATHS[@]}")

(FCStd/LFS model files not included — stored on gitea)"

git -C "$TMP_WORKTREE" commit -q -m "$MSG"

echo "Sync commit ready:"
git -C "$TMP_WORKTREE" log --oneline -1
echo ""

if [[ $DRY_RUN -eq 1 ]]; then
    echo "(dry run — not pushing)"
    exit 0
fi

echo "Pushing to $REMOTE/$REMOTE_BRANCH..."
GIT_LFS_SKIP_PUSH=1 git -C "$TMP_WORKTREE" push --force-with-lease "$REMOTE" "HEAD:$REMOTE_BRANCH"
echo "Done."
