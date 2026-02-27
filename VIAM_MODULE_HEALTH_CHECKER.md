# Viam Module Health Monitor
## Purpose
Automated health assessment system for Viam module repositories. Evaluates dependency currency, configuration compliance, and documentation quality for internal Viam modules.

## Scope
**Internal Viam modules only** - no OSS license checks or public package concerns.

---

## Status Categories

### GREEN - Healthy (Score: 80-100)
- All dependencies current (< 6 months old)
- Viam SDK version compatible
- No known security vulnerabilities
- README follows Viam standards
- Required configuration files present

### YELLOW - Attention Needed (Score: 50-79)
- Dependencies 6-12 months old
- Minor documentation issues
- Non-critical configuration missing
- Viam SDK version slightly outdated

### RED - Critical (Score: < 50)
- Dependencies > 12 months old
- Known security vulnerabilities
- Missing critical files (meta.json, README)
- Viam SDK incompatible or severely outdated
- README non-compliant

---

## Critical Viam-Specific Files

### Required Files
1. **meta.json** - Module metadata
   - Module ID format: `namespace:module-name:model-name`
   - SDK version compatibility
   - Entrypoint definition
   - Model/service declarations

2. **README.md** - Viam-standard documentation (see structure below)
   - Minimum 500 characters
   - Must follow template structure
   - Configuration examples required

3. **Dependency manifest** (language-specific)
   - Python: `requirements.txt` or `pyproject.toml`
   - Go: `go.mod`
   - TypeScript: `package.json`

### Optional but Recommended
- **tests/** directory with test files
- **examples/** directory with usage samples
- **.viam/**, **module.yaml**, or similar Viam config files

---

## Language-Specific Standards

### Python Modules

#### Critical Checks
- [ ] `requirements.txt` or `pyproject.toml` exists
- [ ] Python version specified (3.8+ recommended)
- [ ] **All dependencies have exact version pins** (no `>=` or `~`)
- [ ] Viam Python SDK present: `viam-sdk==X.Y.Z`
- [ ] Dependencies < 6 months old (YELLOW if 6-12, RED if >12)

#### Viam SDK Compatibility
````python
# Check for Viam SDK in requirements
viam-sdk==0.5.0  # Must be present and reasonably current
````

#### Scoring Deductions
- Missing version pin: **-10 per dependency**
- Dependency 6-12 months old: **-5 each**
- Dependency >12 months old: **-15 each**
- No Python version specified: **-10**
- Viam SDK missing: **-30**
- Viam SDK >6 months outdated: **-20**

---

### Go Modules

#### Critical Checks
- [ ] `go.mod` exists
- [ ] Go version specified (1.20+ recommended)
- [ ] Dependencies use semantic versioning (v1.2.3)
- [ ] Viam RDK present: `go.viam.com/rdk vX.Y.Z`
- [ ] Minimal use of pseudo-versions (e.g., `v0.0.0-20230123...`)

#### Viam SDK Compatibility
````go
require (
    go.viam.com/rdk v0.28.0  // Must be present
    go.viam.com/utils v0.1.0 // Often required
)
````

#### Scoring Deductions
- Pseudo-version dependency: **-5 each**
- Dependency >12 months old: **-15 each**
- No Go version specified: **-10**
- Viam RDK missing: **-30**
- Viam RDK >6 months outdated: **-20**
- Excessive indirect dependencies (>20): **-10**

---

### TypeScript/Node Modules

#### Critical Checks
- [ ] `package.json` exists
- [ ] Lock file present (`package-lock.json` or `yarn.lock`)
- [ ] Node version specified in `engines`
- [ ] Required scripts defined: `test`, `build`
- [ ] Viam SDK present: `@viamrobotics/sdk`

#### Viam SDK Compatibility
````json
{
  "dependencies": {
    "@viamrobotics/sdk": "^0.20.0"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "scripts": {
    "test": "jest",
    "build": "tsc"
  }
}
````

#### Scoring Deductions
- No lock file: **-20**
- Missing test script: **-10**
- Missing build script: **-10**
- Version ranges too loose (^, ~): **-5 per major dependency**
- Viam SDK missing: **-30**
- Viam SDK >6 months outdated: **-20**

---

## README Structure Validation

### Required Structure

#### 1. Title (Required)
````markdown
# Module {module-name}
````
**Format:** Single H1, starts with "Module "

#### 2. Overview Paragraph (Required)
- Minimum 100 characters
- Describes module purpose and use case
- Technical approach summary

#### 3. Key Capabilities (Recommended)
````markdown
**Key capabilities:** feature1, feature2, feature3

**Output:** what module produces
````

#### 4. Model Declaration (Required)
````markdown
## Model `{namespace}:{module-name}:{model-name}`
````
**Validation:**
- Must use backticks
- Format: `namespace:module:model` (colon-separated)
- Common namespaces: `viam`, `viam-labs`, org-specific

#### 5. Description Section (Required)
````markdown
### Description
````
Detailed technical explanation of functionality

#### 6. Configuration Section (Required)
Must include:
- [ ] Prose explanation of configuration
- [ ] JSON schema template
- [ ] Attributes table with columns: Name, Type, Inclusion, Description
- [ ] At least one example configuration (valid JSON)

**Required Attributes Table Format:**
````markdown
#### Attributes

| Name | Type | Inclusion | Description |
|------|------|-----------|-------------|
| `param` | str | Required | Description |
````

**Example Configuration Required:**
````markdown
#### Example Configuration

Minimal configuration:
```json
{
  "required_param": "value"
}
```

Full configuration:
```json
{
  "required_param": "value",
  "optional_param": 42
}
```
````

#### 7. DoCommand Section (If Applicable)
For modules with administrative commands:
````markdown
### DoCommand

#### Supported commands

- command_name — description
```json
  {"command": "command_name"}
```
````

---

## README Validation Checklist

### Structure (40 points)
- [ ] Title with `# Module {name}` format **(10 pts)**
- [ ] Overview paragraph >100 chars **(5 pts)**
- [ ] Model declaration with proper namespace **(10 pts)**
- [ ] Configuration section present **(10 pts)**
- [ ] At least one example configuration **(5 pts)**

### Formatting (30 points)
- [ ] Code elements in backticks **(5 pts)**
- [ ] Attributes table with required columns **(10 pts)**
- [ ] Valid JSON in all examples **(10 pts)**
- [ ] Consistent heading hierarchy **(5 pts)**

### Content Quality (30 points)
- [ ] Type annotations for all parameters **(10 pts)**
- [ ] Required/Optional specified for attributes **(10 pts)**
- [ ] Example configs are valid and runnable **(10 pts)**

**Scoring:**
- 35-40 pts: GREEN (excellent docs)
- 25-34 pts: YELLOW (acceptable, needs minor fixes)
- <25 pts: RED (non-compliant, major issues)

---

## Analysis Execution Flow

### Phase 1: File Discovery
````
1. Check for meta.json
2. Identify language from dependency manifest
3. Scan for README.md
4. Collect additional Viam config files
````

### Phase 2: Dependency Analysis
````
For each language:
  1. Extract dependency list
  2. Check for Viam SDK presence and version
  3. Validate version pinning/formatting
  4. Flag outdated dependencies (>6 months)
  5. Check for security vulnerabilities (if CVE data available)
````

### Phase 3: README Validation
````
1. Parse markdown structure
2. Validate required sections present
3. Check model namespace format
4. Validate configuration tables
5. Parse and validate JSON examples
6. Score against checklist (70 total points)
````

### Phase 4: Meta.json Validation (If Applicable)
````
1. Parse JSON structure
2. Validate module ID format
3. Check SDK version compatibility
4. Verify entrypoint exists
````

### Phase 5: Scoring & Status Assignment
````
Calculate composite score:
  - Dependency health: 40%
  - README compliance: 30%
  - Viam SDK compatibility: 20%
  - Configuration files: 10%

Assign status: GREEN/YELLOW/RED
Generate actionable recommendations
````

---

## Analysis Output Format

### Per-Module Report (JSON)
````json
{
  "module_name": "sonar-blob-detector",
  "overall_status": "YELLOW",
  "health_score": 72,
  "last_checked": "2025-02-03T10:30:00Z",
  
  "viam_specific": {
    "meta_json_present": true,
    "meta_json_valid": true,
    "module_id": "viam:sonar-blob-detector:sonar-blob-service",
    "viam_sdk_status": "GREEN",
    "viam_sdk_version": "0.5.0",
    "viam_sdk_latest": "0.5.2",
    "viam_sdk_age_months": 2
  },
  
  "languages": {
    "python": {
      "status": "YELLOW",
      "files_found": ["requirements.txt"],
      "dependency_count": 12,
      "dependencies_unpinned": 2,
      "dependencies_outdated": 3,
      "python_version": "3.9",
      "issues": [
        "numpy==1.24.0 is 8 months old (current: 1.26.2)",
        "opencv-python has no version pin",
        "pillow has no version pin"
      ],
      "recommendations": [
        "Pin opencv-python: opencv-python==4.8.1.78",
        "Pin pillow: pillow==10.1.0",
        "Update numpy: numpy==1.26.2"
      ]
    }
  },
  
  "readme": {
    "status": "GREEN",
    "score": 38,
    "max_score": 40,
    "structure_valid": true,
    "model_declaration_valid": true,
    "configuration_examples_valid": true,
    "issues": [
      "Missing 'Flow' subsection (recommended but not required)"
    ],
    "recommendations": []
  },
  
  "compliance": {
    "has_meta_json": true,
    "has_readme": true,
    "readme_compliant": true,
    "viam_sdk_present": true,
    "viam_sdk_compatible": true,
    "dependencies_pinned": false,
    "dependencies_current": false
  },
  
  "security": {
    "vulnerabilities_found": 0,
    "vulnerable_packages": []
  }
}
````

---

## Recommendations Format

### Actionable, Specific Guidance

**Good Example:**
````
"Update viam-sdk from 0.4.0 to 0.5.2: pip install viam-sdk==0.5.2"
"Add version pin for opencv-python: opencv-python==4.8.1.78"
"README missing model declaration. Add: ## Model `viam:module:service`"
````

**Bad Example:**
````
"Dependencies are outdated"
"Fix README"
"Update SDK"
````

### Prioritized Issue List

1. **Critical** (RED, blocking issues)
   - Missing meta.json
   - Viam SDK missing or incompatible
   - Security vulnerabilities
   - README non-existent or severely non-compliant

2. **Important** (YELLOW, should fix soon)
   - Dependencies >6 months old
   - Missing version pins
   - README minor issues
   - Viam SDK outdated but compatible

3. **Nice-to-have** (GREEN, optional improvements)
   - Missing optional sections (Flow, examples)
   - Test coverage improvements
   - Documentation enhancements

---

## Claude Analysis Prompt Template
````
You are analyzing a Viam module for health and compliance.

Module: {module_name}
Language: {language}
Repository: {repo_url}

FILES PROVIDED:
1. meta.json: {meta_json_contents}
2. {dependency_file}: {dependency_contents}
3. README.md: {readme_contents}

ANALYSIS REQUIRED:

1. VIAM SDK CHECK
   - Is Viam SDK present and what version?
   - Is it compatible with latest? (check meta.json if provided)
   - Age of SDK version

2. DEPENDENCY HEALTH
   - List all dependencies and their versions
   - Identify unpinned dependencies
   - Flag dependencies >6 months old (YELLOW) or >12 months (RED)
   - Check for security issues if CVE data available

3. README COMPLIANCE
   - Validate structure against Viam template
   - Check for required sections
   - Validate model declaration format
   - Score configuration examples
   - Verify JSON validity

4. META.JSON VALIDATION (if provided)
   - Module ID format correct?
   - Entrypoint defined?
   - SDK version specified?

PROVIDE OUTPUT AS JSON:
{
  "overall_status": "GREEN|YELLOW|RED",
  "health_score": 0-100,
  "viam_specific": {...},
  "languages": {...},
  "readme": {...},
  "compliance": {...},
  "security": {...}
}

Include specific, actionable recommendations.
Prioritize Viam SDK compatibility and README compliance.
````

---

## Tool Requirements

### What Claude Needs

1. **Current date/time** - to calculate dependency age
2. **Web search access** - to check latest SDK versions
3. **File reading** - to parse meta.json, requirements, README
4. **JSON validation** - to verify config examples

### What Claude Cannot Determine Alone

1. **CVE/security data** - needs external security database
2. **Private Viam SDK versions** - may need internal registry access
3. **Organization policies** - custom version requirements
4. **Runtime compatibility** - actual testing required

---

## Edge Cases & Special Handling

### Monorepos
- Multiple modules in single repo
- Check each meta.json separately
- Shared dependencies at root level

### Module Types
- Vision services
- Sensor modules
- Motor controllers
- ML models
- Handle type-specific requirements

### SDK Pre-release Versions
- Alpha/beta versions acceptable if documented
- Check meta.json for version constraints
- Flag if using outdated pre-release

### Custom Registries
- Internal Viam package repositories
- May not match public SDK versions
- Document source in analysis

---

## Usage Notes

### When to Re-analyze
- After dependency updates
- Before module release/promotion
- Monthly health checks
- After Viam SDK major releases

### Integration Points
- CI/CD pipeline checks
- Pre-commit hooks for README validation
- Automated PR comments with health status
- Dashboard for fleet-wide module health

### False Positive Handling
- Allow exceptions list for approved old dependencies
- Custom thresholds per module type
- Override flags in meta.json or config

---

## Success Metrics

A well-maintained Viam module should have:
- Health score >80 (GREEN status)
- Viam SDK within 3 months of latest
- All dependencies pinned and <6 months old
- README scoring >35/40 points
- Zero security vulnerabilities
- Valid, runnable configuration examples

---

*Last updated: 2025-02-03*
*For Viam internal use only*