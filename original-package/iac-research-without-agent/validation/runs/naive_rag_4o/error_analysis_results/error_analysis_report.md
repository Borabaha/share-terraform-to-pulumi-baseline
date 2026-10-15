# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 240 (52.40%)
- **Failed Scripts**: 218 (47.60%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 220
- **Average Errors per Failed Script (Init/Plan)**: 1.62
- **Median Errors per Failed Script (Init/Plan)**: 1.00
- **Maximum Errors in a Script (Init/Plan)**: 6

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 88 | 64.71% |
| 2 | 27 | 19.85% |
| 3 | 11 | 8.09% |
| 4 | 6 | 4.41% |
| 5 | 3 | 2.21% |
| 6 | 1 | 0.74% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| Plan | 126 | 27.51% |
| OPA | 82 | 17.90% |
| Init | 10 | 2.18% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 190 | 86.36% |
| Runtime | 28 | 12.73% |
| Other | 2 | 0.91% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 81 | 36.82% |
| Unsupported Block | 35 | 15.91% |
| Missing Required Argument | 27 | 12.27% |
| File Not Found | 19 | 8.64% |
| Insufficient Required Blocks | 17 | 7.73% |
| Version Constraint | 9 | 4.09% |
| Unsupported Resource | 6 | 2.73% |
| Unsupported Attribute | 5 | 2.27% |
| Invalid Resource Reference | 5 | 2.27% |
| Invalid Argument | 4 | 1.82% |
| Resource: aws_elasticache_user | 3 | 1.36% |
| Resource: aws_db_instance | 3 | 1.36% |
| Unclassified | 2 | 0.91% |
| Resource: aws_eip | 2 | 0.91% |
| Too Many Blocks | 1 | 0.45% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_db_instance | 30 | 15.00% |
| aws_kinesis_firehose_delivery_stream | 18 | 9.00% |
| aws_lambda_function | 16 | 8.00% |
| aws_codebuild_project | 14 | 7.00% |
| aws_route53_record | 13 | 6.50% |
| aws_lex_bot | 10 | 5.00% |
| aws_sagemaker_domain | 10 | 5.00% |
| aws_elastic_beanstalk_environment | 9 | 4.50% |
| aws_connect_instance | 6 | 3.00% |
| aws_mskconnect_custom_plugin | 6 | 3.00% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 10 (2.18% of all scripts)
- **Average Errors per Failed Script**: 1.10
- **Total Distinct Errors**: 11

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Runtime | 9 | 81.82% |
| Other | 2 | 18.18% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Version Constraint | 9 | 81.82% |
| Unclassified | 2 | 18.18% |

### Plan Stage Failures

- **Total Scripts with Failures**: 126 (27.51% of all scripts)
- **Average Errors per Failed Script**: 1.66
- **Total Distinct Errors**: 209

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 190 | 90.91% |
| Runtime | 19 | 9.09% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 81 | 38.76% |
| Unsupported Block | 35 | 16.75% |
| Missing Required Argument | 27 | 12.92% |
| File Not Found | 19 | 9.09% |
| Insufficient Required Blocks | 17 | 8.13% |
| Unsupported Resource | 6 | 2.87% |
| Unsupported Attribute | 5 | 2.39% |
| Invalid Resource Reference | 5 | 2.39% |
| Invalid Argument | 4 | 1.91% |
| Resource: aws_elasticache_user | 3 | 1.44% |

### OPA Stage Failures

- **Total Scripts with Failures**: 82 (17.90% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 82 (17.90% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_db_instance

Total errors: 30

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 30 | 100.00% |

### aws_kinesis_firehose_delivery_stream

Total errors: 18

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 18 | 100.00% |

### aws_lambda_function

Total errors: 16

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 16 | 100.00% |

### aws_codebuild_project

Total errors: 14

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 14 | 100.00% |

### aws_route53_record

Total errors: 13

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 13 | 100.00% |


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
