# Pipeline Orchestrator

A flexible, production-grade orchestration framework for managing complex multi-stage data processing pipelines. This orchestrator was designed to handle enterprise-scale transformations with robust error handling, comprehensive logging, and real-time progress tracking.

## 🎯 Overview

This project demonstrates the design and implementation of a sophisticated pipeline orchestration system that manages the end-to-end execution of multi-phase data processing workflows. The framework emphasizes reliability, observability, and user experience.

## 🏗️ Architecture

### Core Design Principles

1. **Phase-Based Execution**: Organized into distinct, sequential phases that can be executed independently or as part of a complete pipeline
2. **Fail-Fast Error Handling**: Each phase validates success before proceeding, with detailed error reporting
3. **Comprehensive Logging**: Timestamped logs for every operation, enabling audit trails and debugging
4. **Selective Artifact Management**: Only successfully processed artifacts are promoted to subsequent phases
5. **Metrics-Driven Reporting**: Real-time calculation and reporting of success rates and quality metrics

### Pipeline Phases

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐     ┌───────────────┐     ┌───────┐
│  EXTRACT    │ --> │  VALIDATE    │ --> │ ANALYZE  │ --> │  TRANSFORM    │ --> │ BUILD │
└─────────────┘     └──────────────┘     └──────────┘     └───────────────┘     └───────┘
     │                    │                    │                   │                   │
     v                    v                    v                   v                   v
  Obtain raw        Clean and          Analyze deps       Convert to          Compile and
  source files      validate data      and patterns       target format        package
```

### Key Components

#### 1. **PipelineOrchestrator Class**
The core orchestration engine that manages:
- Phase execution sequencing
- Command execution with subprocess management
- Log file generation and management
- Artifact validation and copying
- Metrics calculation and reporting

#### 2. **Execution Modes**
Three flexible execution modes for different use cases:

- **Analysis Only**: Quick analysis without transformation (ideal for assessment)
- **Transform and Build**: Direct transformation and compilation (for rapid iteration)
- **Full Pipeline**: Complete end-to-end execution with all phases

#### 3. **Logging Infrastructure**
- Unique timestamped log files for each operation
- Centralized log directory (`runlogs/`)
- Automatic log rotation and cleanup
- Structured output for parsing and automation

#### 4. **Quality Control**
- Parses transformation logs to identify zero-error artifacts
- Implements selective copying based on quality criteria
- Calculates transformation and build success rates
- Provides detailed metrics reporting

## 🚀 Features

### Production-Ready Capabilities

- ✅ **Interactive Mode Selection**: User-friendly interface for choosing execution workflows
- ✅ **Robust Error Handling**: Graceful failures with detailed error messages
- ✅ **Progress Tracking**: Real-time feedback during long-running operations
- ✅ **Artifact Validation**: Automatic quality checks before promotion
- ✅ **Metrics Reporting**: Comprehensive success rate calculations
- ✅ **Build Tool Integration**: Seamless integration with ANT, Maven, or other build systems
- ✅ **Environment Variable Management**: Configurable execution contexts
- ✅ **Snapshot Support**: Multiple data version management

## 📋 Usage

### Basic Execution

```bash
python pipeline_orchestrator.py
```

### Interactive Workflow

1. **Enter project directory**: Path to your project root
2. **Select snapshot**: Choose from available data snapshots
3. **Enter application name**: Identifier for this execution
4. **Choose execution mode**:
   - `1` - Analysis Only
   - `2` - Transform and Build
   - `3` - Full Pipeline
   - `4` - Exit

### Example Session

```
============================================================
PIPELINE ORCHESTRATOR
============================================================

Enter project directory path: /path/to/project

Available snapshots:
  1. snapshot-1
  2. snapshot-2
  
Select snapshot (or press Enter for default): 1

Enter application name: my_application

Execution Modes:
  1. Analysis Only
  2. Transform and Build
  3. Full Pipeline (Analysis + Transform + Build)
  4. Exit

Select mode: 3

✓ Selected: Full Pipeline

============================================================
PHASE 1: EXTRACTION
============================================================

✓ Extracting source-files completed
✓ Extracting config-files completed
✓ Extracting data-files completed
✓ Extracting metadata completed

...

============================================================
PIPELINE EXECUTION SUMMARY
============================================================

Total Artifacts Processed:    150
Successful Transformations:   145
Artifacts Built:              142

Transformation Success Rate:  96.67%
Build Success Rate:           94.67%

============================================================

✓ Pipeline completed successfully
Total execution time: 324.56 seconds
```

## 🔧 Technical Implementation

### Command Execution

Each phase executes pipeline tools via subprocess with:
- Shell command execution
- Working directory management
- Output redirection to log files
- Exit code validation

### Log Management

```python
log_file = f"{script_name}_{timestamp}.log"
full_cmd = f"{cmd} > \"{log_file}\" 2>&1"
```

### Artifact Quality Control

Artifacts are validated using regex parsing of transformation logs:
```python
pattern = re.compile(r"\|\s*([^|]+\.\w+)\s*\|\s*0\s*\|")
```

Only artifacts with zero errors are promoted to the target directory.

### Metrics Calculation

Success rates are calculated as:
```
Success Rate = (Successful Artifacts / Total Artifacts) × 100%
```

Two key metrics are tracked:
1. **Transformation Success Rate**: Percentage of artifacts transformed without errors
2. **Build Success Rate**: Percentage of artifacts successfully compiled

## 📁 Project Structure

```
project/
├── pipeline_orchestrator.py    # Main orchestrator
├── runlogs/                     # Execution logs (timestamped)
├── tools/
│   └── pipeline/                # Pipeline tool scripts
│       ├── extract-*.py
│       ├── validate-*.py
│       ├── analyze-*.py
│       └── transform-*.py
├── deliveries/                  # Input data snapshots
│   ├── snapshot-1/
│   └── snapshot-2/
├── work/                        # Intermediate artifacts
│   └── transformed/
├── target/                      # Final build artifacts
│   └── artifacts/
└── logs/                        # Transformation logs
    └── transformation.log
```

## 🎓 Design Decisions

### Why Phase-Based Architecture?
- **Separation of Concerns**: Each phase has a single responsibility
- **Testability**: Phases can be tested independently
- **Flexibility**: Users can execute specific phases as needed
- **Debugging**: Easier to isolate issues to specific phases

### Why Selective Artifact Copying?
- **Quality Assurance**: Only validated artifacts proceed to build
- **Resource Efficiency**: Avoids wasting build time on known failures
- **Clear Metrics**: Success rates reflect actual usable output

### Why Timestamped Logging?
- **Audit Trail**: Complete history of all executions
- **Parallel Execution**: Prevents log file conflicts
- **Debugging**: Easy to correlate issues with specific runs

## 🛠️ Extensibility

The framework is designed to be extended:

1. **Add New Phases**: Inherit from `PipelineOrchestrator` and add new phase methods
2. **Custom Build Tools**: Modify `_execute_build()` to support additional tools
3. **Advanced Metrics**: Extend `_calculate_metrics()` for domain-specific KPIs
4. **Notification Integration**: Add hooks for Slack, email, or other notifications

### Example: Adding a New Phase

```python
def deploy_phase(self, environment: str) -> bool:
    """Deploy artifacts to specified environment."""
    print(f"\n{'='*60}")
    print(f"PHASE 6: DEPLOYMENT TO {environment.upper()}")
    print(f"{'='*60}\n")
    
    cmd = f"python tools/pipeline/deploy-to-{environment}.py"
    rc = self.run_command(cmd, f"Deploying to {environment}")
    
    return rc == 0
```

## 📊 Performance Characteristics

- **Scalability**: Handles projects with 1000+ source files
- **Reliability**: Fail-fast design prevents cascading failures
- **Observability**: Complete execution visibility through logs and metrics
- **User Experience**: Clear progress indicators and actionable error messages

## 🎯 Use Cases

This orchestration pattern is applicable to various domains:

- **Data Migration Projects**: Multi-stage data transformation pipelines
- **Code Modernization**: Legacy system conversion workflows
- **ETL Pipelines**: Extract-Transform-Load operations
- **Build Automation**: Complex multi-step build processes
- **Testing Frameworks**: Sequential test suite execution

## 📝 License

MIT License - Feel free to use this pattern in your own projects.

## 👤 Author

This orchestration framework was designed and implemented to manage enterprise-scale data processing pipelines, emphasizing production reliability, observability, and maintainability.

---

**Note**: This is a generalized framework. The actual implementation was used in a production environment to orchestrate complex transformation pipelines for enterprise applications.
