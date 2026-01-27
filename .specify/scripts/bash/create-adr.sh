#!/bin/bash

# Create Architecture Decision Record
# Usage: ./create-adr.sh "<title>"

TITLE="$1"
DATE=$(date +%Y-%m-%d)
ADR_DIR="history/adr"

# Find next available ID
ID=1
while [ -f "$ADR_DIR/$ID-"* ]; do
    ID=$((ID + 1))
done

# Generate slug from title (lowercase, replace spaces with hyphens, remove special chars)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

# Create ADR file
ADR_FILE="$ADR_DIR/$ID-$SLUG.md"

# Write template
cat > "$ADR_FILE" << EOF
# ADR-$ID: $TITLE

**Status**: Proposed
**Date**: $DATE
**Context**: Phase 3 AI Assistant Integration

---

## Context

[PROBLEM STATEMENT - What situation led to this decision?]

---

## Decision

[THE CHOSEN APPROACH - Describe what was decided and all its components]

---

## Alternatives Considered

1. **[Alternative 1]** - [One sentence summary]
   - **Pros**: [Advantages]
   - **Cons**: [Disadvantages compared to chosen approach]

2. **[Alternative 2]** - [One sentence summary]
   - **Pros**: [Advantages]
   - **Cons**: [Disadvantages compared to chosen approach]

---

## Consequences

**Positive**:
- [Benefits of this decision]

**Negative**:
- [Drawbacks or risks introduced by this decision]

**Neutral**:
- [Other impacts or requirements]

---

## References

- [Link to relevant documentation]
- [Link to discussions or issues]

---
EOF

echo "{\"adr_path\": \"$ADR_FILE\", \"adr_id\": $ID, \"slug\": \"$SLUG\"}"
