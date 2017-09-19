#!/usr/bin/env bash
# This is a sample IFTTT action for pinging an arbitrary domain. You almost
# definitely won't use this. If you do find some need to include this in your
# workflow... I'd love to know why.
set -euo pipefail

# CONFIGURATION
# default values
COUNT="1"

# cli overrides
while getopts 'c:' flag; do
  case "${flag}" in
    c) COUNT="${OPTARG}"                 ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

# sanity check
# NOTE: you can use environment variables from your IFTTT image. No need to pass
# constants explicitly!
[[ -z "${DOMAIN}" ]] && { error "DOMAIN is unset" }
[[ -z "${COUNT}" ]] && { error "COUNT is unset" }
#

# ACTION
# Because we set `euo pipefail` above, this action script will exit with a
# non-zero exit code if the below ping command fails. This is a good thing if
# you want any insight into whether your action succeeded. If the action returns
# zero, IFTTT will assume everything is kosher :)
ping -c${COUNT} ${DOMAIN}
