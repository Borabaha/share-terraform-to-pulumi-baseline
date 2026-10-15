# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 124 (27.07%)
- **Failed Scripts**: 334 (72.93%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 774
- **Average Errors per Failed Script (Init/Plan)**: 2.69
- **Median Errors per Failed Script (Init/Plan)**: 2.00
- **Maximum Errors in a Script (Init/Plan)**: 17

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 110 | 38.19% |
| 2 | 82 | 28.47% |
| 3 | 30 | 10.42% |
| 4 | 18 | 6.25% |
| 5 | 14 | 4.86% |
| 6 | 14 | 4.86% |
| 7 | 4 | 1.39% |
| 8 | 3 | 1.04% |
| 9 | 3 | 1.04% |
| 10 | 4 | 1.39% |
| 11 | 1 | 0.35% |
| 12 | 2 | 0.69% |
| 13 | 1 | 0.35% |
| 17 | 1 | 0.35% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| Plan | 269 | 58.73% |
| OPA | 46 | 10.04% |
| Init | 19 | 4.15% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 731 | 94.44% |
| Runtime | 31 | 4.01% |
| Syntax | 12 | 1.55% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 326 | 42.12% |
| Missing Required Argument | 140 | 18.09% |
| Unsupported Block | 104 | 13.44% |
| Insufficient Required Blocks | 64 | 8.27% |
| Unsupported Resource | 44 | 5.68% |
| File Not Found | 23 | 2.97% |
| Invalid Argument | 13 | 1.68% |
| Duplicate Resource | 12 | 1.55% |
| Invalid Resource Reference | 10 | 1.29% |
| Format Constraint | 8 | 1.03% |
| Duplicate Provider Configuration | 6 | 0.78% |
| Unsupported Attribute | 5 | 0.65% |
| Duplicate Argument | 4 | 0.52% |
| Invalid HCL | 4 | 0.52% |
| Invalid Attribute | 3 | 0.39% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_lex_bot | 69 | 9.15% |
| aws_lightsail_database | 49 | 6.50% |
| aws_msk_cluster | 38 | 5.04% |
| aws_lambda_function | 32 | 4.24% |
| aws_db_instance | 31 | 4.11% |
| aws_codebuild_project | 27 | 3.58% |
| aws_kinesis_firehose_delivery_stream | 26 | 3.45% |
| aws_chime_voice_connector | 25 | 3.32% |
| aws_elasticache_user | 23 | 3.05% |
| aws_elastic_beanstalk_environment | 17 | 2.25% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 19 (4.15% of all scripts)
- **Average Errors per Failed Script**: 2.00
- **Total Distinct Errors**: 38

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 26 | 68.42% |
| Runtime | 8 | 21.05% |
| Syntax | 4 | 10.53% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Duplicate Resource | 12 | 31.58% |
| Duplicate Provider Configuration | 6 | 15.79% |
| Unsupported Argument | 6 | 15.79% |
| Duplicate Argument | 4 | 10.53% |
| Invalid HCL | 4 | 10.53% |
| Unsupported Block | 2 | 5.26% |
| Invalid Resource Reference | 2 | 5.26% |
| Version Constraint | 1 | 2.63% |
| Provider Not Found | 1 | 2.63% |

### Plan Stage Failures

- **Total Scripts with Failures**: 269 (58.73% of all scripts)
- **Average Errors per Failed Script**: 2.74
- **Total Distinct Errors**: 736

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 705 | 95.79% |
| Runtime | 23 | 3.12% |
| Syntax | 8 | 1.09% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 320 | 43.48% |
| Missing Required Argument | 140 | 19.02% |
| Unsupported Block | 102 | 13.86% |
| Insufficient Required Blocks | 64 | 8.70% |
| Unsupported Resource | 44 | 5.98% |
| File Not Found | 23 | 3.12% |
| Invalid Argument | 13 | 1.77% |
| Format Constraint | 8 | 1.09% |
| Invalid Resource Reference | 8 | 1.09% |
| Unsupported Attribute | 5 | 0.68% |

### OPA Stage Failures

- **Total Scripts with Failures**: 46 (10.04% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 46 (10.04% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_lex_bot

Total errors: 69

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 69 | 100.00% |

### aws_lightsail_database

Total errors: 49

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 49 | 100.00% |

### aws_msk_cluster

Total errors: 38

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 38 | 100.00% |

### aws_lambda_function

Total errors: 32

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 16 | 50.00% |
| Schema | 16 | 50.00% |

### aws_db_instance

Total errors: 31

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 28 | 90.32% |
| Syntax | 3 | 9.68% |


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
