# Persona Simulation Guide

## Constructing a Persona

Every persona in a roundtable is a simulated user archetype. Each persona must have a defined profile before they speak.

### Required Profile Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| **Name** | A realistic first name — humanizes the character | "Maya" |
| **Role** | Job title or relationship to the product | "Senior Marketing Manager" |
| **Goals** | What they're trying to accomplish (2-3 bullets) | "Run campaigns faster", "Reduce tool-switching" |
| **Frustrations** | Pain points with current state (2-3 bullets) | "Too many clicks to publish", "Reports are confusing" |
| **Tech Comfort** | Scale: Novice / Intermediate / Power User | "Intermediate — comfortable with dashboards, avoids APIs" |
| **Context** | Usage patterns, environment, constraints | "Uses the product daily, manages a team of 5, on a tight budget" |

### Optional Enrichments

- **Quote** — A one-liner that captures their attitude: *"I just want it to work without reading a manual."*
- **Tools they use** — Adjacent products they compare against
- **Decision authority** — Can they buy/approve, or do they need sign-off?

## Voice Guidelines

When a persona speaks, they must sound like a real person with that profile — not like an AI analyzing user needs.

### Do This

- Use first person: "I would..." / "That frustrates me because..."
- Reference their specific context: "On my team, we..."
- Show emotion: enthusiasm, skepticism, confusion, excitement
- Ask naive questions if their tech comfort is low
- Push back on complexity if they're a casual user
- Demand power features if they're a power user

### Avoid This

- Third-person analysis: "Users like me would..." (too detached)
- Technical jargon beyond their comfort level
- Perfectly balanced pros/cons lists (real people have biases)
- Agreement with everything (real people have preferences)

## Common Archetypes

Use these as starting points. Customize for the specific product/domain.

### The Power User
- Tech Comfort: Power User
- Goals: Efficiency, automation, keyboard shortcuts, customization
- Frustrations: "Dumbed down" interfaces, missing advanced options, forced workflows
- Voice: Direct, opinionated, references competitor features, wants API access

### The Casual User
- Tech Comfort: Novice to Intermediate
- Goals: Get the task done quickly, minimal learning curve
- Frustrations: Overwhelming interfaces, unclear labels, hidden features
- Voice: Asks "what does this do?", values simplicity, easily overwhelmed

### The Administrator
- Tech Comfort: Intermediate to Power User
- Goals: Control, security, compliance, user management, audit trails
- Frustrations: Lack of permissions granularity, poor audit logs, no bulk operations
- Voice: Risk-conscious, asks about edge cases, thinks about scale

### The New User
- Tech Comfort: Novice
- Goals: Onboarding success, quick time-to-value, not feeling stupid
- Frustrations: No guidance, assumed knowledge, empty states with no direction
- Voice: Uncertain, asks basic questions, compares to familiar tools

### The Stakeholder
- Tech Comfort: Novice (doesn't use the product directly)
- Goals: ROI, adoption metrics, competitive positioning, cost control
- Frustrations: Can't get clear reports, unclear value proposition, budget pressure
- Voice: Business-focused, asks "what's the impact?", wants metrics and outcomes

### The Accessibility User
- Tech Comfort: Varies
- Goals: Full product access with assistive technology, keyboard navigation, screen reader support
- Frustrations: Unlabeled buttons, focus traps, color-only indicators, time-limited interactions
- Voice: Practical, specific about barriers, values standards compliance

## Authenticity Checks

The BA should verify personas are behaving realistically:

1. **Consistency** — Does the persona's reaction match their profile? A novice user shouldn't suggest API integrations.
2. **Distinctness** — Are personas giving different perspectives, or are they all saying the same thing?
3. **Conflict** — If all personas agree, something is wrong. Real user groups have competing needs.
4. **Specificity** — Vague reactions ("that sounds good") aren't useful. Push for concrete scenarios.
5. **Emotional range** — Not every reaction should be calm and rational. Frustration, excitement, and confusion are valid.

## Custom Personas

When the user provides custom persona names/roles, construct their profile by:
1. Inferring reasonable attributes from their role and the discussion topic
2. Stating the inferred profile at the start of their first contribution
3. Asking the user for corrections if the inference feels wrong
