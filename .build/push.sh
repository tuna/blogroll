#!/bin/bash

if [[ $TRAVIS_BRANCH != "master" ]] || [[ $TRAVIS_REPO_SLUG != "tuna/blogroll" ]]; then
  echo "Skip deployment"
  exit 0
fi

# Reference: https://gist.github.com/willprice/e07efd73fb7f13f917ea

scriptpath=$(readlink "$0")
basedir=$(dirname $(dirname "$scriptpath"))

cd "$basedir"

git config --global user.email "ci@travis-ci.org"
git config --global user.name "Travis CI"

git remote add origin-travis https://${GH_TOKEN}@github.com/${TRAVIS_REPO_SLUG}


git fetch origin-travis
git add opml.xml
git stash

git checkout origin-travis/gh-pages || git checkout --orphan gh-pages
git checkout stash -- opml.xml
git reset
git add opml.xml
git commit -m "Travis build: $TRAVIS_BUILD_NUMBER"
git push origin-travis HEAD:gh-pages
