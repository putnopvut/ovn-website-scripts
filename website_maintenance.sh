#!/bin/bash

support_file=$(mktemp -q /tmp/supported_releases.XXXXXX) || exit 1
trap "rm -f $support_file" EXIT
cp supported_branches.txt $support_file

while IFS= read -r line; do
    ./update_website.py $line
done <$support_file
