# Pipeline Orchestrator User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Project Structure Setup](#project-structure-setup)
   - [Launching the Orchestrator](#launching-the-orchestrator)
3. [Pipeline Overview](#pipeline-overview)
4. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
   - [Step 1: Launch and Configuration](#step-1-launch-and-configuration)
   - [Step 2: Select Data Snapshot](#step-2-select-data-snapshot)
   - [Step 3: Choose Execution Mode](#step-3-choose-execution-mode)
5. [Pipeline Phases In Detail](#pipeline-phases-in-detail)
   - [Phase 1: Extract](#phase-1-extract)
   - [Phase 2: Validate](#phase-2-validate)
   - [Phase 3: Analyze](#phase-3-analyze)
   - [Phase 4: Transform](#phase-4-transform)
   - [Phase 5: Build](#phase-5-build)
6. [Understanding Output and Logs](#understanding-output-and-logs)
7. [Execution Metrics](#execution-metrics)
8. [Troubleshooting](#troubleshooting)
9. [Appendix: Environment Variables](#appendix-environment-variables)

---

## Introduction

The Pipeline Orchestrator is a multi-phase automation framework designed to process, transform, and build enterprise application artifacts. It provides a structured approach to handling complex data processing workflows with built-in logging, error handling, and progress tracking.

This guide walks you through each step of using the orchestrator, from initial setup to understanding the final output.

---

## Getting Started

### Prerequisites

Before running the orchestrator, ensure you have:

| Requirement | Description |
|-------------|-------------|
| **Python** | Version 3.7 or higher |
| **Build Tool** | Ant, Maven, or Gradle (for build phase) |
| **Disk Space** | Sufficient space for source files, logs, and artifacts |
| **Permissions** | Read/write access to project directories |

### Project Structure Setup

Your project directory must follow this structure:

```
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT DIRECTORY                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📁 deliveries/                                            │
│   │   └── 📁 snapshot-1/        ← Source data snapshots     │
│   │   └── 📁 snapshot-2/                                    │
│   │                                                         │
│   📁 tools/                                                 │
│   │   └── 📁 pipeline/          ← Processing scripts        │
│   │       ├── extract-*.py                                  │
│   │       ├── validate-*.py                                 │
│   │       ├── analyze-*.py                                  │
│   │       └── transform-*.py                                │
│   │                                                         │
│   📁 work/                                                  │
│   │   └── 📁 transformed/       ← Intermediate results      │
│   │                                                         │
│   📁 target/                                                │
│   │   └── 📁 artifacts/         ← Final build outputs       │
│   │                                                         │
│   📁 logs/                      ← Execution logs            │
│       └── transformation.log                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Launching the Orchestrator

```bash
python pipeline_orchestrator.py
```

---

## Pipeline Overview

The orchestrator executes a **5-phase pipeline**. Here is the complete flow:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE FLOW DIAGRAM                              │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   PHASE 1   │     │   PHASE 2   │     │   PHASE 3   │     │   PHASE 4   │     │   PHASE 5   │
    │   EXTRACT   │────▶│  VALIDATE   │────▶│   ANALYZE   │────▶│  TRANSFORM  │────▶│    BUILD    │
    └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
          │                   │                   │                   │                   │
          ▼                   ▼                   ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐       ┌───────────┐       ┌───────────┐
    │• source   │       │• source   │       │• depend-  │       │• source → │       │• clean    │
    │  files    │       │  files    │       │  encies   │       │  target   │       │• build    │
    │• config   │       │• config   │       │• patterns │       │• config → │       │• install  │
    │  files    │       │  files    │       │• metrics  │       │  target   │       │           │
    │• data     │       │• data     │       │• quality  │       │• data →   │       │           │
    │  files    │       │  files    │       │           │       │  target   │       │           │
    │• metadata │       │           │       │           │       │           │       │           │
    └───────────┘       └───────────┘       └───────────┘       └───────────┘       └───────────┘

```

### Execution Modes

The orchestrator offers **3 execution modes**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION MODES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MODE 1: Analysis Only                                                      │
│  ┌─────────┐   ┌──────────┐   ┌─────────┐                                   │
│  │ EXTRACT │──▶│ VALIDATE │──▶│ ANALYZE │                                   │
│  └─────────┘   └──────────┘   └─────────┘                                   │
│                                                                             │
│  MODE 2: Transform and Build                                                │
│  ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌───────┐                     │
│  │ EXTRACT │──▶│ VALIDATE │──▶│ TRANSFORM │──▶│ BUILD │                     │
│  └─────────┘   └──────────┘   └───────────┘   └───────┘                     │
│                                                                             │
│  MODE 3: Full Pipeline                                                      │
│  ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌───────────┐   ┌───────┐       │
│  │ EXTRACT │──▶│ VALIDATE │──▶│ ANALYZE │──▶│ TRANSFORM │──▶│ BUILD │       │
│  └─────────┘   └──────────┘   └─────────┘   └───────────┘   └───────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Walkthrough

### Step 1: Launch and Configuration

When you run `python pipeline_orchestrator.py`, you will see:

```
============================================================
PIPELINE ORCHESTRATOR
============================================================

Enter project directory path: _
```

**Action:** Enter the full path to your project directory.

**Example:**
```
Enter project directory path: /home/user/my-enterprise-project
```

**What happens:**
- The orchestrator validates the directory exists
- If invalid, you'll see: `❌ Directory '/path' not found. Exiting.`

---

### Step 2: Select Data Snapshot

If your project has a `deliveries/` folder with snapshots:

```
Available snapshots:
  1. snapshot-1
  2. snapshot-2
  3. snapshot-2024-Q4

Select snapshot (or press Enter for default): _
```

**Action:** Enter the number of your desired snapshot, or press Enter for default.

**Next, enter the application name:**

```
Enter application name: _
```

**Example:**
```
Enter application name: inventory-system
```

---

### Step 3: Choose Execution Mode

```
Execution Modes:
  1. Analysis Only
  2. Transform and Build
  3. Full Pipeline (Analysis + Transform + Build)
  4. Exit

Select mode: _
```

**Mode Selection Guide:**

| Mode | When to Use | Phases Executed |
|------|-------------|------------------|
| **1** | Initial assessment, code review, dependency mapping | Extract → Validate → Analyze |
| **2** | Ready to convert and build artifacts | Extract → Validate → Transform → Build |
| **3** | Complete end-to-end processing | All 5 phases |
| **4** | Exit without processing | None |

**After selection:**
```
✓ Selected: Full Pipeline
```

---

## Pipeline Phases In Detail

### Phase 1: Extract

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 1: EXTRACT                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PURPOSE: Discover and extract source files from the delivery snapshot     │
│                                                                              │
│   ┌─────────────────┐                      ┌─────────────────┐               │
│   │   DELIVERIES    │                      │    EXTRACTED    │               │
│   │    SNAPSHOT     │  ═══════════════▶    │      FILES      │               │
│   │                 │     Extraction       │                 │               │
│   │  • Raw sources  │                      │  • source-files │               │
│   │  • Configs      │                      │  • config-files │               │
│   │  • Data files   │                      │  • data-files   │               │
│   │  • Metadata     │                      │  • metadata     │               │
│   └─────────────────┘                      └─────────────────┘               │
│                                                                              │
│   SCRIPTS EXECUTED:                                                          │
│   • tools/pipeline/extract-source-files.py                                   │
│   • tools/pipeline/extract-config-files.py                                   │
│   • tools/pipeline/extract-data-files.py                                     │
│   • tools/pipeline/extract-metadata.py                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Console Output:**
```
============================================================
PHASE 1: EXTRACTION
============================================================

✓ Extracting source-files completed
✓ Extracting config-files completed
✓ Extracting data-files completed
✓ Extracting metadata completed

Extraction Summary:
----------------------------------------
  1. source-files
  2. config-files
  3. data-files
  4. metadata
```

**Failure Handling:**
- If any extraction fails: `❌ Extracting [type] failed.`
- Pipeline stops and exits with error code 1

---

### Phase 2: Validate

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 2: VALIDATE                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PURPOSE: Clean and validate extracted files for quality assurance         │
│                                                                              │
│   ┌─────────────────┐                      ┌─────────────────┐               │
│   │    EXTRACTED    │                      │    VALIDATED    │               │
│   │      FILES      │  ═══════════════▶    │      FILES      │               │
│   │                 │     Validation       │                 │               │
│   │  • May have     │                      │  • Clean        │               │
│   │    errors       │                      │  • Verified     │               │
│   │  • Unverified   │                      │  • Ready for    │               │
│   │    format       │                      │    analysis     │               │
│   └─────────────────┘                      └─────────────────┘               │
│                                                                              │
│   VALIDATION CHECKS:                                                         │
│   ✓ File format verification                                                 │
│   ✓ Syntax validation                                                        │
│   ✓ Encoding checks                                                          │
│   ✓ Completeness verification                                                │
│                                                                              │
│   SCRIPTS EXECUTED:                                                          │
│   • tools/pipeline/validate-source-files.py                                  │
│   • tools/pipeline/validate-config-files.py                                  │
│   • tools/pipeline/validate-data-files.py                                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Console Output:**
```
============================================================
PHASE 2: VALIDATION
============================================================

✓ Validating source-files completed
✓ Validating config-files completed
✓ Validating data-files completed

Validation Summary:
----------------------------------------
  1. source-files
  2. config-files
  3. data-files
```

---

### Phase 3: Analyze

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 3: ANALYZE                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PURPOSE: Analyze dependencies, patterns, and quality metrics              │
│                                                                              │
│   ┌─────────────────┐                      ┌─────────────────┐               │
│   │    VALIDATED    │                      │    ANALYSIS     │               │
│   │      FILES      │  ═══════════════▶    │     REPORTS     │               │
│   │                 │      Analysis        │                 │               │
│   │                 │                      │  • Dependencies │               │
│   │                 │                      │  • Patterns     │               │
│   │                 │                      │  • Metrics      │               │
│   │                 │                      │  • Quality      │               │
│   └─────────────────┘                      └─────────────────┘               │
│                                                                              │
│   ANALYSIS TYPES:                                                            │
│   ┌────────────────┬─────────────────────────────────────────┐               │
│   │ dependencies   │ Maps file relationships and imports     │               │
│   │ patterns       │ Identifies code patterns and structures │               │
│   │ metrics        │ Calculates complexity and size metrics  │               │
│   │ quality        │ Assesses code quality indicators        │               │
│   └────────────────┴─────────────────────────────────────────┘               │
│                                                                              │
│   SCRIPTS EXECUTED:                                                          │
│   • tools/pipeline/analyze-dependencies.py                                   │
│   • tools/pipeline/analyze-patterns.py                                       │
│   • tools/pipeline/analyze-metrics.py                                        │
│   • tools/pipeline/analyze-quality.py                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Console Output:**
```
============================================================
PHASE 3: ANALYSIS
============================================================

✓ Analyzing dependencies completed
✓ Analyzing patterns completed
✓ Analyzing metrics completed
✓ Analyzing quality completed

Analysis Summary:
----------------------------------------
  1. dependencies
  2. patterns
  3. metrics
  4. quality
```

**Note:** For Mode 1 (Analysis Only), the pipeline ends here with:
```
✓ Analysis complete.

Total execution time: 45.32 seconds
```

---

### Phase 4: Transform

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             PHASE 4: TRANSFORM                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PURPOSE: Convert source files to target format/architecture               │
│                                                                              │
│   ┌─────────────────┐                      ┌─────────────────┐               │
│   │     SOURCE      │                      │     TARGET      │               │
│   │     FORMAT      │  ═══════════════▶    │     FORMAT      │               │
│   │                 │   Transformation     │                 │               │
│   │  source-files   │──────────────────────│  target-format  │               │
│   │  config-files   │──────────────────────│  target-config  │               │
│   │  data-files     │──────────────────────│  target-schema  │               │
│   └─────────────────┘                      └─────────────────┘               │
│                                                                              │
│   TRANSFORMATION MAPPING:                                                    │
│   ┌──────────────────┬────────────────────┐                                  │
│   │ Source           │ Target             │                                  │
│   ├──────────────────┼────────────────────┤                                  │
│   │ source-files     │ target-format      │                                  │
│   │ config-files     │ target-config      │                                  │
│   │ data-files       │ target-schema      │                                  │
│   └──────────────────┴────────────────────┘                                  │
│                                                                              │
│   OUTPUT LOCATION: work/transformed/                                         │
│                                                                              │
│   SCRIPTS EXECUTED:                                                          │
│   • tools/pipeline/transform-source-files-to-target-format.py                │
│   • tools/pipeline/transform-config-files-to-target-config.py                │
│   • tools/pipeline/transform-data-files-to-target-schema.py                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Console Output:**
```
============================================================
PHASE 4: TRANSFORMATION
============================================================

✓ Transforming source-files to target-format completed
✓ Transforming config-files to target-config completed
✓ Transforming data-files to target-schema completed

Transformation Summary:
----------------------------------------
  1. source-files → target-format
  2. config-files → target-config
  3. data-files → target-schema
```

---

### Phase 5: Build

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                               PHASE 5: BUILD                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   PURPOSE: Compile and package validated artifacts                          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │                         BUILD PROCESS                               │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   STEP 1: Identify Successful Artifacts                                      │
│   ┌─────────────────┐                                                        │
│   │ Parse logs/     │──▶ Find artifacts with 0 errors                       │
│   │ transformation  │                                                        │
│   │ .log            │                                                        │
│   └─────────────────┘                                                        │
│           │                                                                  │
│           ▼                                                                  │
│   STEP 2: Copy Validated Artifacts                                           │
│   ┌─────────────────┐         ┌─────────────────┐                            │
│   │ work/           │ ──────▶ │ target/         │                            │
│   │ transformed/    │  Copy   │ artifacts/      │                            │
│   └─────────────────┘         └─────────────────┘                            │
│           │                                                                  │
│           ▼                                                                  │
│   STEP 3: Execute Build Tool                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐    │
│   │  ant clean  ──▶  ant build  ──▶  ant install                        │    │
│   └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Console Output:**
```
============================================================
PHASE 5: BUILD
============================================================

Copying validated artifacts to target directory...
✓ Copied 42 validated artifacts

Building artifacts using ANT...

✓ ant clean
✓ ant build
✓ ant install
```

**If build tool not found:**
```
⚠ ant not found, skipping build step.
```

---

## Understanding Output and Logs

### Log File Location

All execution logs are stored in the `runlogs/` directory:

```
runlogs/
├── extract-source-files_1699876543.log
├── extract-config-files_1699876544.log
├── validate-source-files_1699876550.log
├── transform-source-files-to-target-format_1699876560.log
├── ant_clean_1699876580.log
├── ant_build_1699876585.log
└── ant_install_1699876590.log
```

**Log Naming Convention:** `{script-name}_{unix-timestamp}.log`

### Transformation Log Format

The `logs/transformation.log` contains results in a table format:

```
| Artifact Name      | Errors | Warnings |
|--------------------|--------|----------|
| module1.src        | 0      | 2        |  ← Will be copied (0 errors)
| module2.src        | 3      | 1        |  ← Will NOT be copied
| config1.cfg        | 0      | 0        |  ← Will be copied (0 errors)
```

---

## Execution Metrics

At the end of execution, you'll see a summary:

```
============================================================
PIPELINE EXECUTION SUMMARY
============================================================

Total Artifacts Processed:    150
Successful Transformations:   142
Artifacts Built:              142

Transformation Success Rate:  94.67%
Build Success Rate:           94.67%

============================================================

✓ Pipeline completed successfully
Total execution time: 127.45 seconds
```

**Metrics Explained:**

| Metric | Description |
|--------|-------------|
| **Total Artifacts Processed** | All files that went through transformation |
| **Successful Transformations** | Files with zero transformation errors |
| **Artifacts Built** | Files successfully copied and built |
| **Transformation Success Rate** | (Successful / Total) × 100 |
| **Build Success Rate** | (Built / Total) × 100 |

---

## Troubleshooting

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `❌ Directory not found` | Invalid project path | Verify the path exists and is accessible |
| `❌ Extracting [type] failed` | Script error or missing files | Check `runlogs/` for detailed error |
| `⚠ ant not found` | Build tool not installed | Install Ant, Maven, or Gradle |
| `Pipeline interrupted by user` | Ctrl+C pressed | Re-run the orchestrator |

### Checking Detailed Logs

1. Navigate to `runlogs/` directory
2. Find the log file for the failed step (by timestamp)
3. Open and review the error details

```bash
cat runlogs/extract-source-files_1699876543.log
```

### Exit Codes

| Code | Meaning |
|------|----------|
| `0` | Success |
| `1` | Failure (check logs for details) |

---

## Appendix: Environment Variables

The orchestrator sets these environment variables during execution:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `DELIVERY_DIR` | Path to selected snapshot | `deliveries/snapshot-1` |
| `SNAPSHOT_NAME` | Name of selected snapshot | `snapshot-1` |
| `APP_NAME` | Application identifier | `inventory-system` |

These variables are available to all pipeline scripts during execution.

---

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           QUICK REFERENCE                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAUNCH:    python pipeline_orchestrator.py                                  │
│                                                                              │
│  MODES:     1 = Analysis Only    (Extract → Validate → Analyze)             │
│             2 = Transform+Build  (Extract → Validate → Transform → Build)   │
│             3 = Full Pipeline    (All 5 phases)                              │
│             4 = Exit                                                         │
│                                                                              │
│  PHASES:    Extract → Validate → Analyze → Transform → Build                │
│                                                                              │
│  LOGS:      runlogs/*.log                                                    │
│                                                                              │
│  OUTPUT:    target/artifacts/                                                │
│                                                                              │
│  SUCCESS:   ✓ = passed    ❌ = failed    ⚠ = warning                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```
