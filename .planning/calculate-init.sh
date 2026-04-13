#!/bin/bash
# Generate init JSON for GSD planning workflow

PHASE="01"
HAS_CONTEXT="true"
HAS_RESEARCH="true"
PHASE_DIR="/Users/dev/Code/School/geospatial-data-processing/.planning/phases/01-map-interaction-user-selection"

cat << INITJSON
{
  "planner_model": "zai-org/GLM-4.7-FP8",
  "researcher_model": "zai-org/GLM-4.7-FP8",
  "checker_model": "zai-org/GLM-4.7-FP8",
  "commit_docs": false,
  "research_enabled": true,
  "phase_dir": "$PHASE_DIR",
  "phase_number": "$PHASE",
  "has_research": $HAS_RESEARCH,
  "has_context": $HAS_CONTEXT,
  "mode": "standard"
}
INITJSON
