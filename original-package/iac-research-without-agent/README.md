# IAC Research Project

This repository contains tools and scripts for Infrastructure as Code (IaC) research.

## Project Structure

```
iac-research/
├── iac_research/               # Main package
│   ├── terraform/              # Terraform-related functionality
│   ├── validation/             # Validation functionality
│   ├── data_processing/        # Data processing utilities 
│   ├── file_operations/        # File management utilities
│   └── utils/                  # Common utilities
├── scripts/                    # Command-line scripts
├── data/                       # Data directory
├── ground_truth/               # Ground truth dataset
├── validation/                 # Validation dir
└── logs/                       # Log files
```

## Installation

1. Clone this repository
2. (Optional) Create a virtual environment
3. Install requirements:
   ```
   pip install -r requirements.txt
   ```

## Common Operations

### Generate Terraform Files from CSV

```bash
python scripts/generate_terraform.py --csv-file data/iac_eval.csv --output-dir validation/generated --mode scripts
```

### Run Terraform Validation

```bash
python scripts/run_validation.py --base-dir validation/dataset
```

### Rerun Failed Validations

```bash
python scripts/rerun_failed.py --previous-results validation/terraform_results.csv
```

### Clean Terraform Files

```bash
python scripts/clean_terraform.py --base-dir validation/generated --operation remove_version_constraint
```

### File Operations

```bash
# Copy directory structure
python scripts/file_operations.py --operation copy_structure --source-dir ground_truth/dataset --target-dir validation/dataset

# Replace main.tf files
python scripts/file_operations.py --operation replace_files --source-dir ground_truth/dataset --target-dir validation/dataset
```

### Analyze OPA Results

```bash
python scripts/analyze_opa.py --base-dir ground_truth/dataset --output-dir ground_truth/results
```

## Module Documentation

### Terraform Module

- `executor.py` - Core functions for executing Terraform commands

### Validation Module

- `runner.py` - Runs Terraform validation
- `analyzer.py` - Analyzes OPA results

### Data Processing Module

- `csv_processor.py` - Processes CSV data
- `terraform_generator.py` - Generates Terraform files

### File Operations Module

- `file_manager.py` - Functions for file operations
- `terraform_cleaner.py` - Cleans Terraform files

### Utils Module

- `logging.py` - Logging configuration
- `reporting.py` - Report generation utilities

## Development
Under development right now.