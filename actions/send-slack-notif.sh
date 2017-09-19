#!/usr/bin/env bash
# This is an IFTTT action for sending a slack notification.
set -euo pipefail

# CONFIGURATION
while getopts 't:' flag; do
  case "${flag}" in
    t) TEXT="${OPTARG}"                  ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

[[ -z "${SLACK_CHANNEL}" ]] && { error "SLACK_CHANNEL is unset" }
[[ -z "${SLACK_WEBHOOK_URL}" ]] && { error "SLACK_WEBHOOK_URL is unset" }
[[ -z "${TEXT}" ]] && { error "TEXT is unset" }
#

PAYLOAD=$(cat <<EOF
{
    "channel": "${SLACK_CHANNEL}",
    "text": "${TEXT}"
}
EOF
)

curl -sS \
     -XPOST \
     -H 'Content-Type: application/json' \
     -d "${PAYLOAD}" \
     "${SLACK_WEBHOOK_URL}"
