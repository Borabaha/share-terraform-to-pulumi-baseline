"""
Analysis tools for OPA (Open Policy Agent) evaluation results.
"""
import os
import json
import subprocess
import csv
import logging
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


def run_opa_eval(directory):
    """
    Run OPA evaluation in the given directory and return the value part.

    Args:
        directory (str): Directory containing tfplan.json and intent.rego files

    Returns:
        dict: OPA evaluation results or None if evaluation failed
    """
    try:
        # Change to the directory
        original_dir = os.getcwd()
        os.chdir(directory)

        # Check if required files exist
        if not os.path.exists('tfplan.json') or not os.path.exists('intent.rego'):
            logger.warning(f"Missing required files in {directory}")
            os.chdir(original_dir)
            return None

        # Run the command
        logger.info(f"Running OPA evaluation in {directory}")
        result = subprocess.run(
            ['opa', 'eval', '-i', 'tfplan.json', '-d', 'intent.rego', 'data'],
            capture_output=True, text=True, check=True
        )

        # Change back to original directory
        os.chdir(original_dir)

        # Parse the JSON output
        output = json.loads(result.stdout)

        # Extract just the "value" part
        if (output and 'result' in output and len(output['result']) > 0 and
                'expressions' in output['result'][0] and len(output['result'][0]['expressions']) > 0):
            return output['result'][0]['expressions'][0]['value']
        return None

    except Exception as e:
        logger.exception(f"Error processing {directory}: {e}")
        # Change back to original directory in case of error
        if os.getcwd() != original_dir:
            os.chdir(original_dir)
        return None


def extract_validation_status(result):
    """
    Extract a simple validation status from a complex OPA result.

    Args:
        result (dict): OPA evaluation result

    Returns:
        bool: True if validation passed, False otherwise
    """
    if not result:
        return False

    # Check for success at any level of nesting
    def check_success_recursive(data):
        if isinstance(data, dict):
            # Direct success indicators
            if 'allow' in data and data['allow'] is True:
                return True
            if 'valid' in data and data['valid'] is True:
                return True

            # Check validation dictionaries
            if 'validation' in data:
                validation_dict = data['validation']
                # If all boolean values in validation dict are True, consider it successful
                bool_values = [v for k, v in validation_dict.items() if isinstance(v, bool) and
                               not (k.startswith('has_') and k.endswith('_required'))]
                if bool_values and all(bool_values):
                    return True

            # Check for keys ending with _valid
            valid_fields = [k for k in data.keys() if k.endswith('_valid') and isinstance(data[k], bool)]
            if valid_fields and all(data[k] for k in valid_fields):
                return True

            # Check cluster_parameter_group_valid and similar patterns
            valid_fields = [k for k in data.keys() if 'valid' in k and isinstance(data[k], bool)]
            if valid_fields and all(data[k] for k in valid_fields):
                return True

            # Generic check for any dictionary of all boolean values that are all True
            # This generalizes handling for terraform and other data structures
            if data:
                bool_fields = [v for k, v in data.items() if isinstance(v, bool)]
                if bool_fields and len(bool_fields) == len(data) and all(bool_fields):
                    return True

            # Special handling for terraform dict with all boolean values = True
            if len(data) == 1 and "terraform" in data:
                terraform_data = data["terraform"]
                if isinstance(terraform_data, dict):
                    bool_fields = [v for k, v in terraform_data.items() if isinstance(v, bool)]
                    if bool_fields and all(bool_fields):
                        return True

            # Recursively check all nested dictionaries
            for key, value in data.items():
                if check_success_recursive(value):
                    return True

        return False

    return check_success_recursive(result)


def extract_success_reason(details):
    """
    Extract a readable success reason from OPA evaluation details.

    Args:
        details (dict): OPA evaluation details

    Returns:
        str: Readable success reason
    """
    # Try to find the most relevant success indicator
    if isinstance(details, dict):
        # Check for terraform-specific boolean fields
        if 'terraform' in details and isinstance(details['terraform'], dict):
            terraform_data = details['terraform']
            # Look for boolean fields in terraform data
            bool_fields = {k: v for k, v in terraform_data.items() if isinstance(v, bool) and v is True}
            if bool_fields:
                field_name = list(bool_fields.keys())[0]
                return f"terraform: {field_name}: True"

        # Check for direct indicators
        if 'allow' in details and details['allow'] is True:
            return "allow: True"
        if 'valid' in details and details['valid'] is True:
            return "valid: True"

        # Check for nested dictionaries
        for key in ['main', 'terraform', 'validation']:
            if key in details and isinstance(details[key], dict):
                nested_reason = extract_success_reason(details[key])
                if nested_reason:
                    return f"{key}: {nested_reason}"

        # Check for validation fields
        validation_fields = {}
        if 'validation' in details and isinstance(details['validation'], dict):
            for k, v in details['validation'].items():
                if isinstance(v, bool) and v is True:
                    validation_fields[k] = v
            if validation_fields:
                return f"validation: {list(validation_fields.keys())[:3]}"

        # Generic check for all boolean values
        bool_fields = {k: v for k, v in details.items() if isinstance(v, bool) and v is True}
        if bool_fields and len(bool_fields) == len(details):
            field_names = list(bool_fields.keys())
            return f"all boolean fields true: {field_names[:3]}"

    # If no specific reason found, return the details
    return str(details)


def analyze_opa_results(base_dir, failed_dirs=None, output_dir=None):
    """
    Analyze OPA evaluation results for directories containing intent.rego and tfplan.json.

    Args:
        base_dir (str): Base directory containing directories to analyze
        failed_dirs (set): Set of directory names to skip (e.g., previously failed)
        output_dir (str): Directory to save output files (defaults to base_dir)

    Returns:
        dict: Results summary
    """
    if failed_dirs is None:
        failed_dirs = set()

    if output_dir is None:
        output_dir = base_dir

    # Store results indexed by directory name
    results = {}

    # Find all directories with intent.rego and tfplan.json files in the base directory
    for root, dirs, files in os.walk(base_dir):
        dir_name = os.path.basename(root)
        if 'intent.rego' in files and 'tfplan.json' in files and dir_name not in failed_dirs:
            logger.info(f"Processing {dir_name}...")
            result = run_opa_eval(root)
            if result:
                success = extract_validation_status(result)
                results[dir_name] = {
                    'success': success,
                    'details': result
                }

    # Organize results by success/failure
    successful_dirs = {}
    failed_dirs_results = {}

    for dir_name, result in results.items():
        if result['success']:
            successful_dirs[dir_name] = result['details']
        else:
            failed_dirs_results[dir_name] = result['details']

    # Create output CSV file path
    output_file = os.path.join(output_dir, 'opa_results.csv')

    # Write results to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Directory', 'Status', 'Details'])

        # Write successful directories
        writer.writerow(['Successful Directories', '', ''])
        for dir_name, details in sorted(successful_dirs.items(), key=lambda x: x[0]):
            # Extract success reason for better readability
            success_reason = extract_success_reason(details)
            writer.writerow([dir_name, 'Success', success_reason])

        # Write failed directories
        writer.writerow(['Failed Directories', '', ''])
        for dir_name, details in sorted(failed_dirs_results.items(), key=lambda x: x[0]):
            writer.writerow([dir_name, 'Failure', str(details)])

    # Create a summary file
    summary_file = os.path.join(output_dir, 'opa_results_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("Successful Directories:\n")
        for dir_name in sorted(successful_dirs.keys()):
            f.write(f"- {dir_name}\n")

        f.write("\nFailed Directories:\n")
        for dir_name in sorted(failed_dirs_results.keys()):
            f.write(f"- {dir_name}\n")

    logger.info(f"Results saved to {output_file}")
    logger.info(f"Summary saved to {summary_file}")

    # Summary statistics
    summary = {
        'total_processed': len(results),
        'successful': len(successful_dirs),
        'failed': len(failed_dirs_results),
        'skipped': len(failed_dirs)
    }

    logger.info(f"Processed {summary['total_processed']} directories:")
    logger.info(f"  - Successful: {summary['successful']}")
    logger.info(f"  - Failed: {summary['failed']}")
    logger.info(f"  - Skipped (previously failed): {summary['skipped']}")

    return summary