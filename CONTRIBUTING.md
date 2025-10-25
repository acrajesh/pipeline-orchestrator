# Contributing to Pipeline Orchestrator

Thank you for your interest in contributing to this project! This document provides guidelines for extending and customizing the orchestrator.

## Extending the Orchestrator

### Adding a New Phase

To add a new phase to the pipeline:

```python
def custom_phase(self, inputs: List[str]) -> bool:
    """
    Execute custom processing phase.
    
    Args:
        inputs: List of input parameters
        
    Returns:
        True if phase succeeds, False otherwise
    """
    print("\n" + "="*60)
    print("PHASE X: CUSTOM PROCESSING")
    print("="*60 + "\n")
    
    for item in inputs:
        desc = f"Processing {item}"
        cmd = f"python tools/pipeline/custom-{item}.py"
        
        rc = self.run_command(cmd, desc)
        if rc != 0:
            print(f"❌ {desc} failed.")
            return False
        
        self.execution_summary['custom'].append(item)
        print(f"✓ {desc} completed")
    
    self._print_phase_summary('custom', 'Custom Processing')
    return True
```

### Adding Custom Metrics

Extend the `_calculate_metrics()` method:

```python
def _calculate_custom_metrics(self) -> Dict:
    """Calculate domain-specific metrics."""
    metrics = self._calculate_metrics(artifacts, count)
    
    # Add custom metrics
    metrics['custom_metric_1'] = self._compute_custom_metric_1()
    metrics['custom_metric_2'] = self._compute_custom_metric_2()
    
    return metrics
```

### Integrating Different Build Tools

Support for additional build tools:

```python
def _execute_build(self, build_tool: str) -> bool:
    """Execute build with different tools."""
    
    build_configs = {
        'ant': ['clean', 'build', 'install'],
        'maven': ['clean', 'compile', 'package', 'install'],
        'gradle': ['clean', 'build', 'test'],
        'make': ['clean', 'all', 'install']
    }
    
    targets = build_configs.get(build_tool, ['build'])
    
    for target in targets:
        # Execute build target
        cmd = f'{build_tool} {target}'
        rc = self._run_build_command(cmd)
        if rc != 0:
            return False
    
    return True
```

### Adding Notifications

Integrate notification systems:

```python
def notify(self, message: str, level: str = "INFO"):
    """Send notifications via configured channels."""
    
    # Email notification
    if self.config.get('email_enabled'):
        self._send_email(message, level)
    
    # Slack notification
    if self.config.get('slack_enabled'):
        self._send_slack(message, level)
    
    # Custom webhook
    if self.config.get('webhook_url'):
        self._send_webhook(message, level)
```

## Configuration-Driven Execution

### Loading Configuration

```python
import yaml

def load_config(config_file: str) -> Dict:
    """Load pipeline configuration from YAML file."""
    with open(config_file) as f:
        return yaml.safe_load(f)

# In main()
config = load_config('pipeline_config.yaml')
orchestrator = PipelineOrchestrator(
    project_dir=config['project_dir'],
    config=config
)
```

### Dynamic Phase Loading

```python
def execute_pipeline(self, mode: str):
    """Execute pipeline based on configuration mode."""
    
    phases = self.config['modes'][mode]['phases']
    
    for phase in phases:
        phase_config = self.config['phases'][phase]
        
        if not phase_config['enabled']:
            continue
        
        phase_method = getattr(self, f"{phase}_phase")
        success = phase_method(**phase_config)
        
        if not success:
            self.notify(f"Phase {phase} failed", level="ERROR")
            return False
    
    return True
```

## Testing

### Unit Tests

```python
import unittest
from pipeline_orchestrator import PipelineOrchestrator

class TestPipelineOrchestrator(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = "/path/to/test/project"
        self.orchestrator = PipelineOrchestrator(self.test_dir)
    
    def test_extract_phase(self):
        """Test extraction phase execution."""
        result = self.orchestrator.extract_phase(['test-files'])
        self.assertTrue(result)
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        metrics = self.orchestrator._calculate_metrics(
            ['file1.src', 'file2.src'],
            2
        )
        self.assertIn('transform_success_rate', metrics)
```

### Integration Tests

```python
def test_full_pipeline():
    """Test complete pipeline execution."""
    orchestrator = PipelineOrchestrator('/path/to/test/project')
    
    # Execute full pipeline
    orchestrator.extract_phase(['source-files'])
    orchestrator.validate_phase(['source-files'])
    orchestrator.analyze_phase(['dependencies'])
    orchestrator.transform_phase([('source', 'target')])
    success, metrics = orchestrator.build_phase()
    
    assert success
    assert metrics['transform_success_rate'] > 0
```

## Best Practices

### 1. Error Handling
Always validate inputs and handle errors gracefully:
```python
if not os.path.exists(project_dir):
    print(f"❌ Directory not found: {project_dir}")
    sys.exit(1)
```

### 2. Logging
Use descriptive log messages:
```python
print(f"✓ Phase completed: {len(items)} items processed")
```

### 3. Progress Indicators
Provide feedback for long operations:
```python
print(f"Processing {i+1}/{total}: {item}")
```

### 4. Metrics
Always calculate and report success rates:
```python
success_rate = (successful / total * 100) if total else 0
print(f"Success rate: {success_rate:.2f}%")
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Write descriptive docstrings
- Keep functions focused and single-purpose
- Use meaningful variable names

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Questions or Suggestions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about usage
- Documentation improvements

Thank you for contributing! 🎉
