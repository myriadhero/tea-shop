#! /usr/bin/bash
# this script should check if new version of the project is available on git
# and rebuild containers if so

git remote update

if git status -uno | grep "Your branch is behind 'origin/main'"; then
    # 1. pull the new version
    git pull

    # 2. build new docker containers
    sh ./utils/dockerrebuild.sh
fi
