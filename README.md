# viam-module-monitor

Automated health monitoring for Viam module repositories. Analyzes dependency currency, SDK compatibility, and documentation compliance using Claude AI.

## Purpose

**Internal Viam tool** - monitors module health without modifying code.

**What it does:**
- Pulls module repos from GitHub
- Analyzes Python, Go, and TypeScript dependencies
- Validates Viam SDK versions and compatibility
- Checks README compliance against Viam standards
- Generates health reports (GREEN/YELLOW/RED status)

**What it does NOT do:**
- Modify code or create PRs
- Run tests or compile code
- Access private registries (uses public package info)

## Quick Start

### Prerequisites
- Python 3.8+
- GitHub personal access token
- Anthropic API key

### Setup

1. **Clone and setup environment:**
```bash 