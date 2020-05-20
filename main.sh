#!/usr/bin/env bash

set -eu

repo_uri="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
remote_name="origin"
main_branch="master"

cd "$GITHUB_WORKSPACE"

git config user.name "$GITHUB_ACTOR"
git config user.email "${GITHUB_ACTOR}@bots.github.com"

git checkout "$main_branch"

mkdir -p tmp

now=$(date +"%Y%m%d")



#python3 -m pip install --upgrade pip
#python3 -m pip install -r script/requirements.txt

python3 script/fetch_data.py

rm -r tmp/
pwd
git add .
set +e  # Grep succeeds with nonzero exit codes to show results.
git status | grep 'new file\|modified'
if [ $? -eq 0 ]
then
    set -e
    git commit -am "data updated on - $now"
    git remote set-url "$remote_name" "$repo_uri" # includes access token
    git push --force-with-lease "$remote_name"  "$main_branch" #"$gh_pages_branch"
else
    set -e
    echo "No changes since last run"
fi

echo "finish"


## source https://github.com/covid19india/api
