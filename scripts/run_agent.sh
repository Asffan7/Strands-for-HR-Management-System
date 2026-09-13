#!/usr/bin/env bash
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
python3 -m app.agentic_workflow.leave_agent