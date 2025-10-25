"""
Multi-Phase Pipeline Orchestrator

A flexible orchestration framework for managing complex multi-stage data processing pipelines.
This orchestrator manages sequential and parallel execution of pipeline stages with robust
error handling, logging, and progress tracking.

Key Features:
- Configurable multi-phase execution (Extract → Validate → Analyze → Transform → Build)
- Interactive mode selection for different execution workflows
- Comprehensive logging with timestamped outputs
- Artifact validation and selective copying based on quality metrics
- Success rate calculation and reporting
- Graceful error handling and user feedback

Author: [Your Name]
License: MIT
"""

import os
import subprocess
import time
import sys
import re
import shutil
import threading
from typing import List, Tuple, Dict, Optional


class PipelineOrchestrator:
    """
    Orchestrates multi-phase pipeline execution with logging, error handling,
    and progress tracking.
    """
    
    def __init__(self, project_dir: str):
        """
        Initialize the orchestrator.
        
        Args:
            project_dir: Root directory of the project to process
        """
        self.project_dir = project_dir
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runlogs")
        self.execution_summary = {
            'extract': [],
            'validate': [],
            'analyze': [],
            'transform': [],
            'build': []
        }
    
    def run_command(self, cmd: str, desc: str, cwd: Optional[str] = None) -> int:
        """
        Execute a shell command with logging and error handling.
        
        Args:
            cmd: Command to execute
            desc: Human-readable description for logging
            cwd: Working directory for command execution
            
        Returns:
            Exit code of the command
        """
        if cwd is None:
            cwd = self.project_dir
            
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Generate unique log file with timestamp
        script_name = cmd.split()[2] if len(cmd.split()) > 2 else cmd.replace(' ', '_')
        script_name = os.path.basename(script_name)
        log_file = os.path.join(
            self.log_dir, 
            f"{os.path.splitext(script_name)[0]}_{int(time.time())}.log"
        )
        
        full_cmd = f"{cmd} > \"{log_file}\" 2>&1"
        exit_code = subprocess.call(full_cmd, shell=True, cwd=cwd)
        
        return exit_code
    
    def extract_phase(self, file_types: List[str]) -> bool:
        """
        Execute extraction phase to obtain source files.
        
        Args:
            file_types: List of file types to extract
            
        Returns:
            True if all extractions succeed, False otherwise
        """
        print("\n" + "="*60)
        print("PHASE 1: EXTRACTION")
        print("="*60 + "\n")
        
        for file_type in file_types:
            desc = f"Extracting {file_type}"
            cmd = f"python tools/pipeline/extract-{file_type}.py"
            
            rc = self.run_command(cmd, desc)
            if rc != 0:
                print(f"❌ {desc} failed.")
                return False
            
            self.execution_summary['extract'].append(file_type)
            print(f"✓ {desc} completed")
        
        self._print_phase_summary('extract', 'Extraction')
        return True
    
    def validate_phase(self, file_types: List[str]) -> bool:
        """
        Execute validation phase to clean and validate extracted files.
        
        Args:
            file_types: List of file types to validate
            
        Returns:
            True if all validations succeed, False otherwise
        """
        print("\n" + "="*60)
        print("PHASE 2: VALIDATION")
        print("="*60 + "\n")
        
        for file_type in file_types:
            desc = f"Validating {file_type}"
            cmd = f"python tools/pipeline/validate-{file_type}.py"
            
            rc = self.run_command(cmd, desc)
            if rc != 0:
                print(f"❌ {desc} failed.")
                return False
            
            self.execution_summary['validate'].append(file_type)
            print(f"✓ {desc} completed")
        
        self._print_phase_summary('validate', 'Validation')
        return True
    
    def analyze_phase(self, analysis_types: List[str]) -> bool:
        """
        Execute analysis phase to analyze dependencies and patterns.
        
        Args:
            analysis_types: List of analysis types to perform
            
        Returns:
            True if all analyses succeed, False otherwise
        """
        print("\n" + "="*60)
        print("PHASE 3: ANALYSIS")
        print("="*60 + "\n")
        
        for analysis_type in analysis_types:
            desc = f"Analyzing {analysis_type}"
            cmd = f"python tools/pipeline/analyze-{analysis_type}.py"
            
            rc = self.run_command(cmd, desc)
            if rc != 0:
                print(f"❌ {desc} failed.")
                return False
            
            self.execution_summary['analyze'].append(analysis_type)
            print(f"✓ {desc} completed")
        
        self._print_phase_summary('analyze', 'Analysis')
        return True
    
    def transform_phase(self, transformations: List[Tuple[str, str]]) -> bool:
        """
        Execute transformation phase to convert files to target format.
        
        Args:
            transformations: List of (source_type, target_type) tuples
            
        Returns:
            True if all transformations succeed, False otherwise
        """
        print("\n" + "="*60)
        print("PHASE 4: TRANSFORMATION")
        print("="*60 + "\n")
        
        for source, target in transformations:
            desc = f"Transforming {source} to {target}"
            cmd = f"python tools/pipeline/transform-{source}-to-{target}.py"
            
            rc = self.run_command(cmd, desc)
            if rc != 0:
                print(f"❌ {desc} failed.")
                return False
            
            self.execution_summary['transform'].append(f"{source} → {target}")
            print(f"✓ {desc} completed")
        
        self._print_phase_summary('transform', 'Transformation')
        return True
    
    def build_phase(self, build_tool: str = "ant") -> Tuple[bool, Dict]:
        """
        Execute build phase to compile and package artifacts.
        
        Args:
            build_tool: Build tool to use (ant, maven, gradle, etc.)
            
        Returns:
            Tuple of (success status, metrics dictionary)
        """
        print("\n" + "="*60)
        print("PHASE 5: BUILD")
        print("="*60 + "\n")
        
        # Parse transformation logs to identify successful transformations
        successful_artifacts = self._identify_successful_artifacts()
        
        # Copy successful artifacts to target directory
        copied_count = self._copy_artifacts(successful_artifacts)
        
        # Execute build process
        build_success = self._execute_build(build_tool)
        
        # Calculate metrics
        metrics = self._calculate_metrics(successful_artifacts, copied_count)
        
        return build_success, metrics
    
    def _identify_successful_artifacts(self) -> List[str]:
        """
        Parse transformation logs to identify artifacts with zero errors.
        
        Returns:
            List of successfully transformed artifact names
        """
        log_file = os.path.join(self.project_dir, 'logs', 'transformation.log')
        if not os.path.exists(log_file):
            return []
        
        successful = []
        # Pattern to match: | artifact_name | 0 | (indicating zero errors)
        pattern = re.compile(r"\|\s*([^|]+\.\w+)\s*\|\s*0\s*\|")
        
        with open(log_file) as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    successful.append(match.group(1))
        
        return successful
    
    def _copy_artifacts(self, successful_artifacts: List[str]) -> int:
        """
        Copy successful artifacts to target directory.
        
        Args:
            successful_artifacts: List of artifact names to copy
            
        Returns:
            Number of files successfully copied
        """
        print("Copying validated artifacts to target directory...")
        
        src_dir = os.path.join(self.project_dir, 'work', 'transformed')
        tgt_dir = os.path.join(self.project_dir, 'target', 'artifacts')
        
        os.makedirs(tgt_dir, exist_ok=True)
        
        successful_basenames = {
            os.path.splitext(os.path.basename(x))[0].lower() 
            for x in successful_artifacts
        }
        
        copied_count = 0
        for root, _, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            dest_dir = os.path.join(tgt_dir, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            for file in files:
                basename = os.path.splitext(file)[0].lower()
                if basename in successful_basenames:
                    shutil.copy(
                        os.path.join(root, file), 
                        os.path.join(dest_dir, file)
                    )
                    copied_count += 1
        
        print(f"✓ Copied {copied_count} validated artifacts\n")
        return copied_count
    
    def _execute_build(self, build_tool: str) -> bool:
        """
        Execute build process using specified build tool.
        
        Args:
            build_tool: Build tool executable name
            
        Returns:
            True if build succeeds, False otherwise
        """
        build_exec = shutil.which(build_tool)
        if not build_exec:
            print(f"⚠ {build_tool} not found, skipping build step.")
            return False
        
        tgt_dir = os.path.join(self.project_dir, 'target', 'artifacts')
        
        print(f"Building artifacts using {build_tool.upper()}...\n")
        
        for target in ['clean', 'build', 'install']:
            cmd = f'{build_exec} {target}'
            log_name = f'{build_tool}_{target}_{int(time.time())}.log'
            log_file = os.path.join(self.log_dir, log_name)
            
            full_cmd = f'{cmd} > "{log_file}" 2>&1'
            rc = subprocess.call(full_cmd, shell=True, cwd=tgt_dir)
            
            status = "✓" if rc == 0 else "❌"
            print(f"{status} {build_tool} {target}")
            
            if rc != 0:
                return False
        
        print()
        return True
    
    def _calculate_metrics(self, successful_artifacts: List[str], 
                          copied_count: int) -> Dict:
        """
        Calculate pipeline success metrics.
        
        Args:
            successful_artifacts: List of successful artifact names
            copied_count: Number of files copied
            
        Returns:
            Dictionary containing metrics
        """
        # Count total artifacts processed
        log_file = os.path.join(self.project_dir, 'logs', 'transformation.log')
        total_artifacts = 0
        
        if os.path.exists(log_file):
            with open(log_file) as f:
                for line in f:
                    if '|' in line and any(ext in line for ext in ['.src', '.dat', '.cfg']):
                        total_artifacts += 1
        
        # Calculate success rates
        transform_rate = (len(successful_artifacts) / total_artifacts * 100) if total_artifacts else 0
        build_rate = (copied_count / total_artifacts * 100) if total_artifacts else 0
        
        return {
            'total_artifacts': total_artifacts,
            'successful_transforms': len(successful_artifacts),
            'copied_artifacts': copied_count,
            'transform_success_rate': transform_rate,
            'build_success_rate': build_rate
        }
    
    def _print_phase_summary(self, phase: str, phase_name: str):
        """Print summary of completed phase."""
        items = self.execution_summary[phase]
        if items:
            print(f"\n{phase_name} Summary:")
            print("-" * 40)
            for idx, item in enumerate(items, 1):
                print(f"  {idx}. {item}")
            print()
    
    def print_final_metrics(self, metrics: Dict):
        """
        Print final pipeline execution metrics.
        
        Args:
            metrics: Dictionary containing pipeline metrics
        """
        print("\n" + "="*60)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*60 + "\n")
        
        print(f"Total Artifacts Processed:    {metrics['total_artifacts']}")
        print(f"Successful Transformations:   {metrics['successful_transforms']}")
        print(f"Artifacts Built:              {metrics['copied_artifacts']}")
        print(f"\nTransformation Success Rate:  {metrics['transform_success_rate']:.2f}%")
        print(f"Build Success Rate:           {metrics['build_success_rate']:.2f}%")
        print("\n" + "="*60 + "\n")


def main():
    """Main orchestration workflow with interactive mode selection."""
    
    print("\n" + "="*60)
    print("PIPELINE ORCHESTRATOR")
    print("="*60 + "\n")
    
    # Get project directory
    project_dir = input("Enter project directory path: ").strip()
    print()
    
    if not os.path.isdir(project_dir):
        print(f"❌ Directory '{project_dir}' not found. Exiting.")
        sys.exit(1)
    
    # Select data snapshot
    deliveries = os.path.join(project_dir, 'deliveries')
    if os.path.exists(deliveries):
        snapshots = [d for d in os.listdir(deliveries) 
                    if os.path.isdir(os.path.join(deliveries, d))]
        
        print("Available snapshots:")
        for i, snap in enumerate(snapshots, 1):
            print(f"  {i}. {snap}")
        print()
        
        snap_choice = input("Select snapshot (or press Enter for default): ").strip()
        snapshot = (snapshots[int(snap_choice)-1] 
                   if snap_choice.isdigit() and 1 <= int(snap_choice) <= len(snapshots) 
                   else 'snapshot-1')
    else:
        snapshot = 'snapshot-1'
    
    print()
    
    # Get application name
    app_name = input("Enter application name: ").strip()
    print()
    
    # Select execution mode
    print("Execution Modes:")
    print("  1. Analysis Only")
    print("  2. Transform and Build")
    print("  3. Full Pipeline (Analysis + Transform + Build)")
    print("  4. Exit")
    print()
    
    mode = input("Select mode: ").strip()
    
    if mode == '4':
        print("Exiting.")
        sys.exit(0)
    
    mode_names = {
        '1': 'Analysis Only',
        '2': 'Transform and Build',
        '3': 'Full Pipeline'
    }
    
    print(f"\n✓ Selected: {mode_names.get(mode, 'Unknown')}\n")
    
    # Set environment variables
    os.environ['DELIVERY_DIR'] = f"deliveries/{snapshot}"
    os.environ['SNAPSHOT_NAME'] = snapshot
    os.environ['APP_NAME'] = app_name
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator(project_dir)
    
    # Clean logs directory
    if os.path.exists(orchestrator.log_dir):
        shutil.rmtree(orchestrator.log_dir)
    os.makedirs(orchestrator.log_dir, exist_ok=True)
    
    # Execute based on selected mode
    start_time = time.time()
    
    try:
        if mode in ('1', '3'):
            # Analysis workflow
            file_types = ['source-files', 'config-files', 'data-files', 'metadata']
            if not orchestrator.extract_phase(file_types):
                sys.exit(1)
            
            validate_types = ['source-files', 'config-files', 'data-files']
            if not orchestrator.validate_phase(validate_types):
                sys.exit(1)
            
            analysis_types = ['dependencies', 'patterns', 'metrics', 'quality']
            if not orchestrator.analyze_phase(analysis_types):
                sys.exit(1)
            
            if mode == '1':
                print("✓ Analysis complete.")
                elapsed = time.time() - start_time
                print(f"\nTotal execution time: {elapsed:.2f} seconds")
                return
        
        if mode in ('2', '3'):
            # Transform and build workflow
            if mode == '2':
                # Need to run extract and validate for mode 2
                file_types = ['source-files', 'config-files', 'data-files', 'metadata']
                if not orchestrator.extract_phase(file_types):
                    sys.exit(1)
                
                validate_types = ['source-files', 'config-files', 'data-files']
                if not orchestrator.validate_phase(validate_types):
                    sys.exit(1)
            
            # Transformation phase
            transformations = [
                ('source-files', 'target-format'),
                ('config-files', 'target-config'),
                ('data-files', 'target-schema')
            ]
            if not orchestrator.transform_phase(transformations):
                sys.exit(1)
            
            # Build phase
            build_success, metrics = orchestrator.build_phase(build_tool='ant')
            
            # Print metrics
            orchestrator.print_final_metrics(metrics)
            
            if build_success:
                print("✓ Pipeline completed successfully")
            else:
                print("⚠ Pipeline completed with warnings")
        
        elapsed = time.time() - start_time
        print(f"Total execution time: {elapsed:.2f} seconds\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
