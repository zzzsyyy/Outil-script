#!/usr/bin/env bash
git rev-list --all | xargs -rL1 git ls-tree -r --long | sort -uk3 | sort -rnk4 | head -${1:10} | awk '{print $1, $2, $3, $4,$5}' | while read -r mode type hash size path; do echo "${mode} ${type} ${hash} $(numfmt --to=iec-i --suffix=B --padding=7 ${size}) ${path}";done

