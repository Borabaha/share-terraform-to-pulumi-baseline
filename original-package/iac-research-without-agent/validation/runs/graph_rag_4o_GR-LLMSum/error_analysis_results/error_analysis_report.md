# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 287 (62.66%)
- **Failed Scripts**: 171 (37.34%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 120
- **Average Errors per Failed Script (Init/Plan)**: 1.56
- **Median Errors per Failed Script (Init/Plan)**: 1.00
- **Maximum Errors in a Script (Init/Plan)**: 7

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 53 | 68.83% |
| 2 | 14 | 18.18% |
| 3 | 6 | 7.79% |
| 4 | 2 | 2.60% |
| 6 | 1 | 1.30% |
| 7 | 1 | 1.30% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| OPA | 94 | 20.52% |
| Plan | 73 | 15.94% |
| Init | 4 | 0.87% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 94 | 78.33% |
| Runtime | 15 | 12.50% |
| Syntax | 6 | 5.00% |
| Other | 5 | 4.17% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 39 | 32.50% |
| Missing Required Argument | 23 | 19.17% |
| File Not Found | 13 | 10.83% |
| Unsupported Block | 12 | 10.00% |
| Format Constraint | 6 | 5.00% |
| Invalid Resource Reference | 5 | 4.17% |
| Unclassified | 5 | 4.17% |
| Invalid Argument | 5 | 4.17% |
| Resource: aws_elasticache_user | 3 | 2.50% |
| Unsupported Resource | 3 | 2.50% |
| Insufficient Required Blocks | 2 | 1.67% |
| Version Constraint | 2 | 1.67% |
| Resource: aws_sagemaker_pipeline | 1 | 0.83% |
| Resource: aws_eip | 1 | 0.83% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_db_instance | 22 | 20.18% |
| aws_lambda_function | 12 | 11.01% |
| aws_kinesis_firehose_delivery_stream | 6 | 5.50% |
| aws_security_group | 6 | 5.50% |
| aws_vpc | 6 | 5.50% |
| aws_route53_record | 4 | 3.67% |
| aws_connect_instance | 4 | 3.67% |
| aws_eks_cluster | 4 | 3.67% |
| aws_sagemaker_domain | 4 | 3.67% |
| aws_elasticache_user | 3 | 2.75% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 4 (0.87% of all scripts)
- **Average Errors per Failed Script**: 2.25
- **Total Distinct Errors**: 9

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 6 | 66.67% |
| Runtime | 2 | 22.22% |
| Other | 1 | 11.11% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Invalid Resource Reference | 4 | 44.44% |
| Version Constraint | 2 | 22.22% |
| Unsupported Block | 2 | 22.22% |
| Unclassified | 1 | 11.11% |

### Plan Stage Failures

- **Total Scripts with Failures**: 73 (15.94% of all scripts)
- **Average Errors per Failed Script**: 1.52
- **Total Distinct Errors**: 111

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 88 | 79.28% |
| Runtime | 13 | 11.71% |
| Syntax | 6 | 5.41% |
| Other | 4 | 3.60% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 39 | 35.14% |
| Missing Required Argument | 23 | 20.72% |
| File Not Found | 13 | 11.71% |
| Unsupported Block | 10 | 9.01% |
| Format Constraint | 6 | 5.41% |
| Invalid Argument | 5 | 4.50% |
| Unclassified | 4 | 3.60% |
| Resource: aws_elasticache_user | 3 | 2.70% |
| Unsupported Resource | 3 | 2.70% |
| Insufficient Required Blocks | 2 | 1.80% |

### OPA Stage Failures

- **Total Scripts with Failures**: 94 (20.52% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 94 (20.52% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_db_instance

Total errors: 22

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 17 | 77.27% |
| Syntax | 5 | 22.73% |

### aws_lambda_function

Total errors: 12

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 11 | 91.67% |
| Schema | 1 | 8.33% |

### aws_kinesis_firehose_delivery_stream

Total errors: 6

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 6 | 100.00% |

### aws_security_group

Total errors: 6

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 6 | 100.00% |

### aws_vpc

Total errors: 6

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 6 | 100.00% |


## Visualizations

The following visualizations are available in the report directory:

- `failure_stage_distribution.png`: Distribution of failures by stage
- `error_category_distribution.png`: Distribution of all errors by category
- `error_count_distribution.png`: Distribution of error counts per script
- `success_failure_pie.png`: Overall success and failure distribution
- `error_subcategory_heatmap.png`: Heatmap of top error subcategories by stage
- `resource_type_errors.png`: Distribution of errors across resource types

## Individual Errors

For detailed analysis, please refer to the following files:

- `error_analysis_results.csv`: Contains script-level aggregated results
- `individual_errors.csv`: Contains all individual errors with details
- `error_samples.csv`: Contains a sample of errors for manual verification
