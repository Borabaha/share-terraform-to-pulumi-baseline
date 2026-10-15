"""
Error analysis tools for Infrastructure as Code evaluation with multi-error support.
"""
import os
import re
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class IaCErrorAnalyzer:
    """Analyzer for Infrastructure as Code errors across multiple validation stages."""

    def __init__(self, terraform_results_path, opa_results_path=None):
        """
        Initialize the error analyzer with paths to result files.

        Args:
            terraform_results_path (str): Path to the Terraform validation results CSV
            opa_results_path (str, optional): Path to the OPA validation results CSV
        """
        self.terraform_results_path = terraform_results_path
        self.opa_results_path = opa_results_path
        self.terraform_df = None
        self.opa_df = None
        self.merged_df = None
        self.patterns = self._load_patterns()
        self.all_errors = []  # List to store individual errors for detailed analysis

    def _load_patterns(self):
        """
        Load error pattern definitions from a JSON file.
        Uses only the subcategory patterns file which contains both category and subcategory information.

        Returns:
            dict: Dictionary of error patterns by category and subcategory
        """
        # Try to load patterns
        try:
            pattern_path = os.path.join(os.path.dirname(__file__), 'taxonomy.json')
            if os.path.exists(pattern_path):
                with open(pattern_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Patterns file not found at {pattern_path}")
                return {}
        except Exception as e:
            logger.warning(f"Could not load error patterns: {e}")
            return {}

    def load_data(self):
        """
        Load the Terraform and OPA results data.

        Returns:
            self: For method chaining
        """
        try:
            # Load Terraform results
            self.terraform_df = pd.read_csv(self.terraform_results_path)

            # Convert Directory to string for consistent joining
            self.terraform_df['Directory'] = self.terraform_df['Directory'].astype(str)

            # Convert boolean columns
            for col in ['Init Success', 'Plan Success']:
                if col in self.terraform_df.columns:
                    self.terraform_df[col] = self.terraform_df[col].map(
                        {'True': True, 'False': False, True: True, False: False})

            logger.info(f"Loaded {len(self.terraform_df)} Terraform validation results")

            # Load OPA results if available
            if self.opa_results_path and os.path.exists(self.opa_results_path):
                self.opa_df = pd.read_csv(self.opa_results_path)
                if 'Directory' in self.opa_df.columns:
                    # Ensure directory is string type
                    self.opa_df['Directory'] = self.opa_df['Directory'].astype(str)
                    logger.info(f"Loaded {len(self.opa_df)} OPA validation results")
                else:
                    logger.warning("OPA results missing Directory column")
            else:
                logger.info("No OPA results provided or file not found")

            return self
        except Exception as e:
            logger.exception(f"Error loading data: {e}")
            raise

    def merge_results(self):
        """
        Merge Terraform and OPA results based on Directory field.

        Returns:
            self: For method chaining
        """
        if self.terraform_df is None:
            self.load_data()

        # Initialize merged dataframe with Terraform results
        self.merged_df = self.terraform_df.copy()

        # Add OPA results if available
        if self.opa_df is not None and 'Directory' in self.opa_df.columns:
            # Get status from OPA results
            opa_status = self.opa_df[['Directory', 'Status']].copy()
            opa_status.columns = ['Directory', 'OPA Status']

            # Merge with Terraform results
            self.merged_df = pd.merge(
                self.merged_df,
                opa_status,
                on='Directory',
                how='left'
            )

            # Fill missing OPA status
            self.merged_df['OPA Status'] = self.merged_df['OPA Status'].fillna('Not Evaluated')

            logger.info(f"Merged dataframe created with {len(self.merged_df)} rows")
        else:
            # No OPA data to merge
            self.merged_df['OPA Status'] = 'Not Evaluated'
            logger.info("No OPA data to merge, using Terraform results only")

        # Add overall status column
        self.merged_df['Overall Status'] = 'Failed'

        # Set overall status to Success only if passed all stages
        mask_success = (
                (self.merged_df['Init Success'] == True) &
                (self.merged_df['Plan Success'] == True) &
                (self.merged_df['OPA Status'] == 'Success')
        )
        self.merged_df.loc[mask_success, 'Overall Status'] = 'Success'

        # Add failure stage column
        self.merged_df['Failure Stage'] = 'None'

        # Determine failure stage
        mask_init_failure = self.merged_df['Init Success'] == False
        mask_plan_failure = (self.merged_df['Init Success'] == True) & (self.merged_df['Plan Success'] == False)
        mask_opa_failure = (self.merged_df['Plan Success'] == True) & (self.merged_df['OPA Status'] != 'Success')

        self.merged_df.loc[mask_init_failure, 'Failure Stage'] = 'Init'
        self.merged_df.loc[mask_plan_failure, 'Failure Stage'] = 'Plan'
        self.merged_df.loc[mask_opa_failure, 'Failure Stage'] = 'OPA'

        return self

    def classify_errors(self):
        """
        Classify errors based on error patterns in the plan output.
        Handles multiple errors per script.

        Returns:
            self: For method chaining
        """
        if self.merged_df is None:
            self.merge_results()

        # Add columns for error classification - now as lists to handle multiple errors
        self.merged_df['Error Categories'] = None
        self.merged_df['Error Subcategories'] = None

        # Add column for error counts
        self.merged_df['Error Count'] = 0

        # Clear all_errors list in case we're re-running
        self.all_errors = []

        # Process each row to classify errors
        for idx, row in self.merged_df.iterrows():
            if row['Failure Stage'] == 'Init' or row['Failure Stage'] == 'Plan':
                # Get error message from plan output
                error_msg = row.get('Plan Output', '')
                if pd.isna(error_msg):
                    error_msg = ''

                # Classify all errors in the message - pass the actual failure stage
                categories, subcategories, error_count, errors = self._classify_all_terraform_errors(
                    error_msg, row['Directory'], row['Failure Stage']
                )

                # Store the error classifications
                self.merged_df.at[idx, 'Error Categories'] = categories
                self.merged_df.at[idx, 'Error Subcategories'] = subcategories
                self.merged_df.at[idx, 'Error Count'] = error_count

                # Add individual errors to the all_errors list
                self.all_errors.extend(errors)

            elif row['Failure Stage'] == 'OPA':
                # OPA errors categorized as intent validation errors
                categories = ['Intent Validation']
                subcategories = ['Intent Not Met'] if row['OPA Status'] in ['Failure', 'Failed'] else ['Not Evaluated']

                self.merged_df.at[idx, 'Error Categories'] = categories
                self.merged_df.at[idx, 'Error Subcategories'] = subcategories
                self.merged_df.at[idx, 'Error Count'] = 1

                # Add to all_errors list
                self.all_errors.append({
                    'Directory': row['Directory'],
                    'Error': 'Intent validation failed',
                    'Error Category': 'Intent Validation',
                    'Error Subcategory': subcategories[0],
                    'Failure Stage': 'OPA',
                    'Resource Type': 'N/A',
                    'Error Details': row.get('OPA Status', 'Unknown')
                })

            elif row['Failure Stage'] == 'None':
                # Successful cases
                self.merged_df.at[idx, 'Error Categories'] = ['None']
                self.merged_df.at[idx, 'Error Subcategories'] = ['None']
                self.merged_df.at[idx, 'Error Count'] = 0

        logger.info(f"Error classification completed. Found {len(self.all_errors)} individual errors.")
        return self

    def _split_errors(self, error_message):
        """
        Split an error message into separate error instances.

        Args:
            error_message (str): The complete error message

        Returns:
            list: List of individual error messages
        """
        if not error_message or pd.isna(error_message):
            return []

        # Pattern to identify individual error blocks
        error_pattern = r"Error:.*?(?=Error:|$)"

        # Find all matches
        errors = re.findall(error_pattern, error_message, re.DOTALL)

        # If no match found but "Error:" is in the message, consider the whole message as one error
        if not errors and "Error:" in error_message:
            return [error_message]

        return errors

    def _classify_all_terraform_errors(self, error_message, directory, failure_stage):
        """
        Classify all errors in a Terraform error message.

        Args:
            error_message (str): The complete error message
            directory (str): The directory of the script with the error
            failure_stage (str): The stage where the failure occurred ('Init' or 'Plan')

        Returns:
            tuple: (list of categories, list of subcategories, error count, list of error details)
        """
        if not error_message or pd.isna(error_message):
            return ['Unknown'], ['No Error Message'], 0, []

        # Split error message into individual errors
        individual_errors = self._split_errors(error_message)

        if not individual_errors:
            return ['Unknown'], ['Unclassified'], 0, []

        # Classify each individual error
        categories = []
        subcategories = []
        error_details = []

        for error in individual_errors:
            category, subcategory, resource_type = self._classify_single_terraform_error(error)
            categories.append(category)
            subcategories.append(subcategory)

            # Extract the actual error line
            error_text = error.strip().split("\n")[0] if error and "\n" in error else error.strip()

            # Add to error details list - using the passed failure_stage
            error_details.append({
                'Directory': directory,
                'Error': error_text,
                'Error Category': category,
                'Error Subcategory': subcategory,
                'Failure Stage': failure_stage,  # Use the actual failure stage from the row
                'Resource Type': resource_type,
                'Error Details': error
            })

        return categories, subcategories, len(individual_errors), error_details

    def _classify_single_terraform_error(self, error_message):
        """
        Classify a single Terraform error message into a category and subcategory.
        Uses the unified patterns structure where category is the top-level key.

        Args:
            error_message (str): A single error message

        Returns:
            tuple: (category, subcategory, resource_type)
        """
        if not error_message or pd.isna(error_message):
            return 'Unknown', 'No Error Message', 'unknown'

        # Extract resource type if present
        resource_type = 'unknown'
        resource_match = re.search(r"resource\s+\"([^\"]+)\"", error_message, re.IGNORECASE)
        if resource_match:
            resource_type = resource_match.group(1)

        # Check against each pattern in the subcategory_patterns.json structure
        for category, subcategories in self.patterns.items():
            for subcategory, patterns in subcategories.items():
                for pattern in patterns:
                    if re.search(pattern, error_message, re.IGNORECASE):
                        return category, subcategory, resource_type

        # Look for resource-specific errors if no pattern matched
        if "resource" in error_message.lower():
            resource_match = re.search(r"resource\s+\"([^\"]+)\"", error_message, re.IGNORECASE)
            if resource_match:
                return 'Schema', f"Resource: {resource_match.group(1)}", resource_type

        # Look for specific attributes with issues
        attribute_match = re.search(r"argument \"([^\"]+)\"", error_message, re.IGNORECASE)
        if attribute_match:
            return 'Schema', f"Attribute: {attribute_match.group(1)}", resource_type

        return 'Other', 'Unclassified', resource_type

    def get_error_statistics(self):
        """
        Generate error statistics from the merged results.
        Now includes statistics on multiple errors per script but excludes 'Intent Validation' from counts.

        Returns:
            dict: Statistics about error categories and stages
        """
        if self.merged_df is None:
            self.classify_errors()

        stats = {}

        # Overall statistics
        total_count = len(self.merged_df)
        success_count = (self.merged_df['Overall Status'] == 'Success').sum()

        stats['overall'] = {
            'total_scripts': total_count,
            'success_count': success_count,
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'failure_count': total_count - success_count,
            'failure_rate': (total_count - success_count) / total_count if total_count > 0 else 0
        }

        # Failure stage statistics
        failure_stages = self.merged_df['Failure Stage'].value_counts().to_dict()
        # Calculate percentages
        failure_stage_pct = {stage: count / total_count
                             for stage, count in failure_stages.items()
                             if stage != 'None'}

        stats['failure_stages'] = {
            'counts': failure_stages,
            'percentages': failure_stage_pct
        }

        # Multi-error statistics
        error_count_stats = self.merged_df['Error Count'].describe().to_dict()
        stats['error_counts'] = {
            'mean': error_count_stats.get('mean', 0),
            'median': error_count_stats.get('50%', 0),
            'max': error_count_stats.get('max', 0),
            'distribution': self.merged_df['Error Count'].value_counts().to_dict()
        }

        # All error categories from individual errors list
        if self.all_errors:
            # Get error counts directly from all_errors, excluding 'Intent Validation'
            all_category_counts = Counter([err['Error Category'] for err in self.all_errors
                                           if err['Error Category'] != 'Intent Validation'])
            all_subcategory_counts = Counter([err['Error Subcategory'] for err in self.all_errors
                                              if err['Error Category'] != 'Intent Validation'])

            # Get resource type counts (excluding Intent Validation)
            resource_type_counts = Counter([err['Resource Type'] for err in self.all_errors
                                            if err['Resource Type'] != 'unknown' and
                                            err['Resource Type'] != 'N/A' and
                                            err['Error Category'] != 'Intent Validation'])
        else:
            # Fallback to merged_df if all_errors is empty
            all_categories = []
            all_subcategories = []

            for idx, row in self.merged_df.iterrows():
                if not isinstance(row['Error Categories'], list):
                    continue

                categories = row['Error Categories']
                subcategories = row['Error Subcategories']

                # Filter out 'Intent Validation' categories
                if categories and subcategories:
                    filtered_categories = [cat for cat in categories if cat != 'Intent Validation']
                    filtered_subcategories = [subcategories[i] for i, cat in enumerate(categories)
                                              if cat != 'Intent Validation']

                    all_categories.extend(filtered_categories)
                    all_subcategories.extend(filtered_subcategories)

            all_category_counts = dict(Counter(all_categories))
            all_subcategory_counts = dict(Counter(all_subcategories))
            resource_type_counts = {}

        stats['error_categories'] = {
            'all_counts': dict(all_category_counts),
            'subcategory_counts': dict(all_subcategory_counts),
            'resource_type_counts': dict(resource_type_counts)
        }

        # Statistics by stage
        stats['by_stage'] = {}

        for stage in ['Init', 'Plan', 'OPA']:
            stage_df = self.merged_df[self.merged_df['Failure Stage'] == stage]

            # Get errors for this stage from all_errors
            stage_errors = [err for err in self.all_errors if err['Failure Stage'] == stage]

            # For OPA stage, we're keeping the Intent Validation category for stage-specific stats
            # For Init and Plan stages, we filter out 'Intent Validation' (though it shouldn't be there)
            if stage != 'OPA':
                stage_errors = [err for err in stage_errors if err['Error Category'] != 'Intent Validation']

            # Get category and subcategory counts for this stage
            stage_category_counts = Counter([err['Error Category'] for err in stage_errors])
            stage_subcategory_counts = Counter([err['Error Subcategory'] for err in stage_errors])

            stats['by_stage'][stage] = {
                'count': len(stage_df),
                'percentage': len(stage_df) / total_count if total_count > 0 else 0,
                'all_categories': dict(stage_category_counts),
                'all_subcategories': dict(stage_subcategory_counts),
                'avg_errors_per_script': stage_df['Error Count'].mean() if len(stage_df) > 0 else 0,
                'total_distinct_errors': len(stage_errors)
            }

        # Resource-specific error statistics (excluding Intent Validation)
        if self.all_errors:
            resource_errors = {}

            for err in self.all_errors:
                # Skip Intent Validation errors
                if err['Error Category'] == 'Intent Validation':
                    continue

                resource_type = err['Resource Type']
                if resource_type not in ['unknown', 'N/A']:
                    if resource_type not in resource_errors:
                        resource_errors[resource_type] = defaultdict(int)

                    resource_errors[resource_type][err['Error Category']] += 1

            stats['resource_errors'] = resource_errors

        return stats

    def generate_error_report(self, output_dir):
        """
        Generate a comprehensive error report including statistics and visualizations.
        Now includes multi-error analysis and individual error records.

        Args:
            output_dir (str): Directory to save report files

        Returns:
            str: Path to the main report file
        """
        if self.merged_df is None:
            self.classify_errors()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get statistics
        stats = self.get_error_statistics()

        # Save detailed results to CSV
        results_path = os.path.join(output_dir, 'error_analysis_results.csv')

        # Convert list columns to strings for CSV export
        export_df = self.merged_df.copy()
        export_df['Error Categories'] = export_df['Error Categories'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) else str(x))
        export_df['Error Subcategories'] = export_df['Error Subcategories'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) else str(x))

        export_df.to_csv(results_path, index=False)

        # Save individual errors to CSV
        if self.all_errors:
            individual_errors_path = os.path.join(output_dir, 'individual_errors.csv')
            individual_errors_df = pd.DataFrame(self.all_errors)

            # Ensure we don't have too-long fields that would break CSV
            if 'Error Details' in individual_errors_df.columns:
                individual_errors_df['Error Details'] = individual_errors_df['Error Details'].apply(
                    lambda x: x[:500] + '...' if isinstance(x, str) and len(x) > 500 else x
                )

            individual_errors_df.to_csv(individual_errors_path, index=False)
            logger.info(f"Saved {len(self.all_errors)} individual errors to {individual_errors_path}")

        # Generate visualizations
        self._generate_visualizations(stats, output_dir)

        # Generate summary report
        report_path = os.path.join(output_dir, 'error_analysis_report.md')
        self._write_summary_report(stats, report_path)

        return report_path

    def _generate_visualizations(self, stats, output_dir):
        """
        Generate visualizations for the error analysis.
        Now includes multi-error visualizations and excludes Intent Validation from general statistics.

        Args:
            stats (dict): Error statistics
            output_dir (str): Directory to save visualization files
        """
        # Set up visualization style
        plt.style.use('ggplot')

        # 1. Failure Stage Distribution
        plt.figure(figsize=(10, 6))
        stages = [stage for stage in stats['failure_stages']['counts'].keys() if stage != 'None']
        counts = [count for stage, count in stats['failure_stages']['counts'].items() if stage != 'None']

        if stages and counts:
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            plt.bar(stages, counts, color=colors[:len(stages)])
            plt.title('Distribution of Failures by Stage')
            plt.xlabel('Failure Stage')
            plt.ylabel('Number of Scripts')
            plt.savefig(os.path.join(output_dir, 'failure_stage_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # 2. Error Category Distribution (all errors excluding Intent Validation)
        plt.figure(figsize=(12, 8))
        categories = [cat for cat in stats['error_categories']['all_counts'].keys()
                      if cat != 'None' and cat != 'Intent Validation']
        cat_counts = [count for cat, count in stats['error_categories']['all_counts'].items()
                      if cat != 'None' and cat != 'Intent Validation']

        # Sort by count
        cat_data = sorted(zip(categories, cat_counts), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in cat_data]
        cat_counts = [item[1] for item in cat_data]

        if categories and cat_counts:
            plt.barh(categories, cat_counts, color='#66b3ff')
            plt.title('Distribution of Errors by Category (Excluding OPA Validation)')
            plt.xlabel('Number of Occurrences')
            plt.ylabel('Error Category')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'error_category_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # 3. Error Count Distribution (for non-OPA failures only)
        init_plan_failures = self.merged_df[self.merged_df['Failure Stage'].isin(['Init', 'Plan'])]
        if len(init_plan_failures) > 0:
            plt.figure(figsize=(10, 6))
            error_counts = init_plan_failures['Error Count'].value_counts().to_dict()
            counts = sorted([(int(count), freq) for count, freq in error_counts.items() if count != 0])

            if counts:
                x = [item[0] for item in counts]
                y = [item[1] for item in counts]

                plt.bar(x, y, color='#99ff99')
                plt.title('Distribution of Error Counts per Script (Init/Plan Failures)')
                plt.xlabel('Number of Errors')
                plt.ylabel('Number of Scripts')
                plt.xticks(x)
                plt.savefig(os.path.join(output_dir, 'error_count_distribution.png'), dpi=300, bbox_inches='tight')
                plt.close()

        # 4. Success/Failure Pie Chart
        plt.figure(figsize=(8, 8))
        labels = ['Success', 'Failed at Init', 'Failed at Plan', 'Failed at OPA']
        sizes = [
            stats['overall']['success_count'],
            stats['by_stage'].get('Init', {}).get('count', 0),
            stats['by_stage'].get('Plan', {}).get('count', 0),
            stats['by_stage'].get('OPA', {}).get('count', 0)
        ]

        if sum(sizes) > 0:
            colors = ['#99ff99', '#ff9999', '#ffcc99', '#66b3ff']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Overall Success and Failure Distribution')
            plt.savefig(os.path.join(output_dir, 'success_failure_pie.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # 5. Error Subcategory Heatmap (excluding Intent Validation)
        # Get top subcategories for each stage
        subcats_by_stage = {}
        for stage in ['Init', 'Plan']:  # Exclude OPA stage
            if stage in stats['by_stage'] and stats['by_stage'][stage]['all_subcategories']:
                subcats = stats['by_stage'][stage]['all_subcategories']
                # Get top 10 subcategories by count
                top_subcats = sorted(subcats.items(), key=lambda x: x[1], reverse=True)[:10]
                subcats_by_stage[stage] = dict(top_subcats)

        # Create combined set of all top subcategories
        all_subcats = set()
        for subcats in subcats_by_stage.values():
            all_subcats.update(subcats.keys())

        # Remove 'Intent Not Met' if it somehow got included
        if 'Intent Not Met' in all_subcats:
            all_subcats.remove('Intent Not Met')

        if all_subcats:
            # Create matrix for heatmap
            subcats_list = sorted(list(all_subcats))
            stages_list = sorted(list(subcats_by_stage.keys()))

            matrix = np.zeros((len(subcats_list), len(stages_list)))

            for i, subcat in enumerate(subcats_list):
                for j, stage in enumerate(stages_list):
                    matrix[i, j] = subcats_by_stage.get(stage, {}).get(subcat, 0)

            plt.figure(figsize=(12, 10))
            sns.heatmap(matrix, annot=True, fmt='g', cmap='Blues',
                        xticklabels=stages_list, yticklabels=subcats_list)
            plt.title('Distribution of Top Error Subcategories by Stage (Excluding OPA)')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'error_subcategory_heatmap.png'), dpi=300, bbox_inches='tight')
            plt.close()

        # 6. Resource Type Error Distribution (excluding Intent Validation)
        if 'resource_type_counts' in stats['error_categories'] and stats['error_categories']['resource_type_counts']:
            # Get top resource types
            top_resources = sorted(
                stats['error_categories']['resource_type_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 resources

            if top_resources:
                plt.figure(figsize=(10, 6))
                resources = [r[0] for r in top_resources]
                counts = [r[1] for r in top_resources]

                plt.bar(resources, counts, color='#66b3ff')
                plt.title('Top Resource Types with Errors (Excluding OPA Validation)')
                plt.xlabel('Resource Type')
                plt.ylabel('Number of Errors')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'resource_type_errors.png'), dpi=300, bbox_inches='tight')
                plt.close()

    def _write_summary_report(self, stats, report_path):
        """
        Write a summary report of the error analysis.
        Now includes multi-error analysis and excludes OPA results from general error statistics.

        Args:
            stats (dict): Error statistics
            report_path (str): Path to save the report
        """
        with open(report_path, 'w') as f:
            f.write("# Infrastructure as Code Error Analysis Report\n\n")

            # Overall statistics
            f.write("## Overall Statistics\n\n")
            f.write(f"- **Total Scripts Analyzed**: {stats['overall']['total_scripts']}\n")
            f.write(
                f"- **Successful Scripts**: {stats['overall']['success_count']} ({stats['overall']['success_rate']:.2%})\n")
            f.write(
                f"- **Failed Scripts**: {stats['overall']['failure_count']} ({stats['overall']['failure_rate']:.2%})\n\n")

            # Error count statistics
            # Count non-OPA errors for this section
            non_opa_errors = [err for err in self.all_errors if err['Error Category'] != 'Intent Validation']

            f.write("## Error Count Statistics (Excluding OPA Validation Errors)\n\n")
            f.write(f"- **Total Individual Errors**: {len(non_opa_errors)}\n")

            # Calculate average errors per failed script for Init and Plan stages only
            init_plan_failures = self.merged_df[self.merged_df['Failure Stage'].isin(['Init', 'Plan'])]
            if len(init_plan_failures) > 0:
                avg_errors = init_plan_failures['Error Count'].mean()
                median_errors = init_plan_failures['Error Count'].median() if hasattr(init_plan_failures['Error Count'],
                                                                                      'median') else init_plan_failures[
                    'Error Count'].quantile(0.5)
                max_errors = init_plan_failures['Error Count'].max()

                f.write(f"- **Average Errors per Failed Script (Init/Plan)**: {avg_errors:.2f}\n")
                f.write(f"- **Median Errors per Failed Script (Init/Plan)**: {median_errors:.2f}\n")
                f.write(f"- **Maximum Errors in a Script (Init/Plan)**: {max_errors:.0f}\n\n")
            else:
                f.write("- **No Init/Plan failures to analyze**\n\n")

            f.write("### Error Count Distribution (Init/Plan Failures)\n\n")
            f.write("| Number of Errors | Number of Scripts | Percentage |\n")
            f.write("|-----------------|------------------|------------|\n")

            if len(init_plan_failures) > 0:
                error_count_dist = init_plan_failures['Error Count'].value_counts().to_dict()
                total_scripts = len(init_plan_failures)

                for count, num_scripts in sorted(error_count_dist.items()):
                    if count != 0:  # Skip scripts with 0 errors
                        percentage = num_scripts / total_scripts
                        f.write(f"| {count} | {num_scripts} | {percentage:.2%} |\n")
            else:
                f.write("| 0 | 0 | 0% |\n")
            f.write("\n")

            # Failure stages
            f.write("## Failure Distribution by Stage\n\n")
            f.write("| Stage | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")

            for stage, count in stats['failure_stages']['counts'].items():
                if stage != 'None':
                    percentage = count / stats['overall']['total_scripts']
                    f.write(f"| {stage} | {count} | {percentage:.2%} |\n")
            f.write("\n")

            # Error categories (all errors excluding Intent Validation)
            f.write("## Error Categories (Excluding OPA Validation)\n\n")
            f.write("This section includes all errors identified across Init and Plan stages.\n\n")
            f.write("| Category | Count | Percentage of All Errors |\n")
            f.write("|----------|-------|-------------------------|\n")

            total_errors = sum(count for cat, count in stats['error_categories']['all_counts'].items() if cat != 'None')
            if total_errors == 0:
                f.write("| No errors found | 0 | 0% |\n")
            else:
                for category, count in sorted(stats['error_categories']['all_counts'].items(), key=lambda x: x[1],
                                              reverse=True):
                    if category != 'None' and category != 'Intent Validation':
                        percentage = count / total_errors if total_errors > 0 else 0
                        f.write(f"| {category} | {count} | {percentage:.2%} |\n")
            f.write("\n")

            # Top error subcategories (excluding Intent Validation)
            f.write("## Top Error Subcategories (Excluding OPA Validation)\n\n")
            f.write("| Subcategory | Count | Percentage of All Errors |\n")
            f.write("|-------------|-------|-------------------------|\n")

            sorted_subcategories = sorted(
                stats['error_categories']['subcategory_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:15]  # Top 15

            if not sorted_subcategories:
                f.write("| No subcategories found | 0 | 0% |\n")
            else:
                for subcategory, count in sorted_subcategories:
                    if subcategory != 'None' and subcategory != 'Unknown' and subcategory != 'Intent Not Met':
                        percentage = count / total_errors if total_errors > 0 else 0
                        f.write(f"| {subcategory} | {count} | {percentage:.2%} |\n")
            f.write("\n")

            # Resource type statistics
            if stats['error_categories']['resource_type_counts']:
                f.write("## Most Common Resource Types with Errors\n\n")
                f.write("| Resource Type | Count | Percentage of Resource Errors |\n")
                f.write("|--------------|-------|------------------------------|\n")

                total_resource_errors = sum(stats['error_categories']['resource_type_counts'].values())

                sorted_resources = sorted(
                    stats['error_categories']['resource_type_counts'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10

                for resource, count in sorted_resources:
                    percentage = count / total_resource_errors if total_resource_errors > 0 else 0
                    f.write(f"| {resource} | {count} | {percentage:.2%} |\n")
                f.write("\n")

            # Detailed analysis by stage
            f.write("## Detailed Analysis by Stage\n\n")

            for stage in ['Init', 'Plan', 'OPA']:
                if stage in stats['by_stage'] and stats['by_stage'][stage]['count'] > 0:
                    f.write(f"### {stage} Stage Failures\n\n")
                    f.write(
                        f"- **Total Scripts with Failures**: {stats['by_stage'][stage]['count']} ({stats['by_stage'][stage]['percentage']:.2%} of all scripts)\n")

                    if stage != 'OPA':
                        f.write(
                            f"- **Average Errors per Failed Script**: {stats['by_stage'][stage]['avg_errors_per_script']:.2f}\n")
                        f.write(
                            f"- **Total Distinct Errors**: {stats['by_stage'][stage]['total_distinct_errors']}\n\n")
                    else:
                        f.write(
                            "- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.\n\n")
                        # Skip the rest of the analysis for OPA stage
                        continue

                    f.write("#### Top Error Categories\n\n")
                    f.write("| Category | Count | Percentage within Stage |\n")
                    f.write("|----------|-------|-------------------------|\n")

                    # Calculate total errors for this stage
                    stage_total_errors = sum(stats['by_stage'][stage]['all_categories'].values())
                    if stage_total_errors == 0:
                        f.write("| No errors found in this stage | 0 | 0% |\n")
                    else:
                        # Sort categories by count
                        sorted_categories = sorted(
                            stats['by_stage'][stage]['all_categories'].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )

                        for category, count in sorted_categories:
                            if category != 'None' and category != 'Intent Validation':
                                percentage = count / stage_total_errors
                                f.write(f"| {category} | {count} | {percentage:.2%} |\n")
                    f.write("\n")

                    f.write("#### Top Error Subcategories\n\n")
                    f.write("| Subcategory | Count | Percentage within Stage |\n")
                    f.write("|-------------|-------|-------------------------|\n")

                    if stage_total_errors == 0:
                        f.write("| No subcategories found in this stage | 0 | 0% |\n")
                    else:
                        # Sort subcategories by count
                        sorted_subcategories = sorted(
                            stats['by_stage'][stage]['all_subcategories'].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:10]  # Top 10

                        for subcategory, count in sorted_subcategories:
                            if subcategory != 'None' and subcategory != 'Unknown' and subcategory != 'Intent Not Met':
                                percentage = count / stage_total_errors
                                f.write(f"| {subcategory} | {count} | {percentage:.2%} |\n")
                    f.write("\n")

            # Add separate section for OPA validation results
            f.write("## OPA Validation Results\n\n")
            f.write(
                "OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.\n\n")

            opa_failures = self.merged_df[self.merged_df['Failure Stage'] == 'OPA']
            f.write(
                f"- **Total OPA Validation Failures**: {len(opa_failures)} ({len(opa_failures) / stats['overall']['total_scripts']:.2%} of all scripts)\n\n")

            # Resource-specific error patterns (excluding Intent Validation)
            if 'resource_errors' in stats and stats['resource_errors']:
                f.write("## Resource-Specific Error Patterns\n\n")
                f.write("This section shows the most common error categories for each resource type.\n\n")

                # Get top resources by total error count
                resource_total_counts = {res: sum(cats.values()) for res, cats in stats['resource_errors'].items()}
                top_resources = sorted(resource_total_counts.items(), key=lambda x: x[1], reverse=True)[:5]

                for resource, count in top_resources:
                    f.write(f"### {resource}\n\n")
                    f.write(f"Total errors: {count}\n\n")
                    f.write("| Error Category | Count | Percentage |\n")
                    f.write("|---------------|-------|------------|\n")

                    # Sort error categories for this resource
                    sorted_cats = sorted(stats['resource_errors'][resource].items(), key=lambda x: x[1], reverse=True)

                    for category, cat_count in sorted_cats:
                        percentage = cat_count / count
                        f.write(f"| {category} | {cat_count} | {percentage:.2%} |\n")
                    f.write("\n")

            # Visualizations reference
            f.write("\n## Visualizations\n\n")
            f.write("The following visualizations are available in the report directory:\n\n")
            f.write("- `failure_stage_distribution.png`: Distribution of failures by stage\n")
            f.write("- `error_category_distribution.png`: Distribution of all errors by category\n")
            f.write("- `error_count_distribution.png`: Distribution of error counts per script\n")
            f.write("- `success_failure_pie.png`: Overall success and failure distribution\n")
            f.write("- `error_subcategory_heatmap.png`: Heatmap of top error subcategories by stage\n")
            f.write("- `resource_type_errors.png`: Distribution of errors across resource types\n")

            # Individual errors reference
            f.write("\n## Individual Errors\n\n")
            f.write("For detailed analysis, please refer to the following files:\n\n")
            f.write("- `error_analysis_results.csv`: Contains script-level aggregated results\n")
            f.write("- `individual_errors.csv`: Contains all individual errors with details\n")
            f.write("- `error_samples.csv`: Contains a sample of errors for manual verification\n")