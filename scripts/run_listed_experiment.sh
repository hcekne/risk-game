#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <line-number> [command-file]" >&2
  exit 2
fi

line_number="$1"
command_file="${2:-scripts/experiment_commands.sh}"

if ! [[ "$line_number" =~ ^[0-9]+$ ]] || [[ "$line_number" -lt 1 ]]; then
  echo "line number must be a positive integer" >&2
  exit 2
fi

if [[ ! -f "$command_file" ]]; then
  echo "command file not found: $command_file" >&2
  exit 2
fi

command="$(sed -n "${line_number}p" "$command_file")"

if [[ -z "$command" ]]; then
  echo "no command found at line $line_number in $command_file" >&2
  exit 2
fi

if [[ "$command" == '#!'* ]] || [[ "$command" =~ ^[[:space:]]*# ]]; then
  echo "line $line_number in $command_file is not an experiment command" >&2
  exit 2
fi

echo "Executing line $line_number from $command_file:"
echo "$command"
exec bash -lc "$command"
