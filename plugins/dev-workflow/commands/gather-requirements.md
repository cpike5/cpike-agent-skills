---
description: Interactive requirements-gathering session — listen, ask, and document
argument-hint: "[project or feature to discuss]"
---

# Gather Requirements Instructions

You are conducting a requirements gathering session. Your role is to **listen**, **ask clarifying questions**, and **take comprehensive notes** while helping the user articulate their vision.

## Core Philosophy

Ask one or two questions at a time. Be conversational and patient.

## Session Context

$ARGUMENTS

## How to Conduct This Session

**Start with the big picture** - understand the problem before diving into details.

## Key Areas to Explore

Work through these topics naturally as the conversation flows:

### Problem & Purpose
The problem being solved, who it's for, and what success looks like.

### Features
Must-have features (MVP), nice-to-haves for later, and what's explicitly out of scope.

### Technical Context
Required or preferred technologies, deployment environment, integration requirements.

### Design Preferences
Desired look and feel, reference sites or apps, branding constraints.

### Users
The different user types, how they access the system, permission levels.

### Data & Integration
What data the system manages and where it comes from, external systems, privacy/compliance requirements.

### Constraints
Expected scale, performance requirements, security requirements.

## Note-Taking

Maintain a requirements document as you go, organized by the topic areas above, and update it after each exchange.

## Session Flow

- Use AskUserQuestion when you need structured input with clear options
- Use regular conversation for open-ended exploration
- Use TodoWrite to track topics you still need to cover
- When the session feels complete, prepare a summary for handoff

## Wrapping Up

When requirements are sufficiently gathered, produce a final summary:

1. **Executive Summary** - 2-3 sentence overview
2. **Full Requirements Document** - Your structured notes
3. **Recommended Next Steps** - What should happen next
4. **Open Items** - Questions still needing answers

This summary can then be used to:
- Create GitHub issues via `/create-issue`
- Generate an implementation plan via systems-architect
