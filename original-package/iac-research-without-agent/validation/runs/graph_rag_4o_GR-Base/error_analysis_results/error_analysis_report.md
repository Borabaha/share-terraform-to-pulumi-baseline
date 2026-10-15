# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 268 (58.52%)
- **Failed Scripts**: 190 (41.48%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 140
- **Average Errors per Failed Script (Init/Plan)**: 1.56
- **Median Errors per Failed Script (Init/Plan)**: 1.00
- **Maximum Errors in a Script (Init/Plan)**: 6

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 58 | 64.44% |
| 2 | 20 | 22.22% |
| 3 | 8 | 8.89% |
| 4 | 3 | 3.33% |
| 6 | 1 | 1.11% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| OPA | 100 | 21.83% |
| Plan | 88 | 19.21% |
| Init | 2 | 0.44% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 112 | 80.00% |
| Runtime | 17 | 12.14% |
| Other | 6 | 4.29% |
| Syntax | 5 | 3.57% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 39 | 27.86% |
| Missing Required Argument | 32 | 22.86% |
| File Not Found | 15 | 10.71% |
| Unsupported Block | 10 | 7.14% |
| Insufficient Required Blocks | 7 | 5.00% |
| Unclassified | 6 | 4.29% |
| Invalid Argument | 6 | 4.29% |
| Format Constraint | 5 | 3.57% |
| Resource: aws_elasticache_user | 3 | 2.14% |
| Resource: aws_eip | 3 | 2.14% |
| Resource: aws_elastic_beanstalk_environment | 2 | 1.43% |
| Invalid Resource Reference | 2 | 1.43% |
| Unsupported Attribute | 2 | 1.43% |
| Version Constraint | 2 | 1.43% |
| Unsupported Resource | 2 | 1.43% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_db_instance | 12 | 9.45% |
| aws_route53_record | 11 | 8.66% |
| aws_lambda_function | 11 | 8.66% |
| aws_kinesis_firehose_delivery_stream | 7 | 5.51% |
| aws_connect_instance | 6 | 4.72% |
| aws_security_group | 6 | 4.72% |
| aws_lex_bot | 5 | 3.94% |
| aws_codebuild_project | 4 | 3.15% |
| aws_s3_bucket_lifecycle_configuration | 4 | 3.15% |
| aws_sagemaker_domain | 4 | 3.15% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 2 (0.44% of all scripts)
- **Average Errors per Failed Script**: 1.00
- **Total Distinct Errors**: 2

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Runtime | 2 | 100.00% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Version Constraint | 2 | 100.00% |

### Plan Stage Failures

- **Total Scripts with Failures**: 88 (19.21% of all scripts)
- **Average Errors per Failed Script**: 1.57
- **Total Distinct Errors**: 138

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 112 | 81.16% |
| Runtime | 15 | 10.87% |
| Other | 6 | 4.35% |
| Syntax | 5 | 3.62% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 39 | 28.26% |
| Missing Required Argument | 32 | 23.19% |
| File Not Found | 15 | 10.87% |
| Unsupported Block | 10 | 7.25% |
| Insufficient Required Blocks | 7 | 5.07% |
| Unclassified | 6 | 4.35% |
| Invalid Argument | 6 | 4.35% |
| Format Constraint | 5 | 3.62% |
| Resource: aws_elasticache_user | 3 | 2.17% |
| Resource: aws_eip | 3 | 2.17% |

### OPA Stage Failures

- **Total Scripts with Failures**: 100 (21.83% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 100 (21.83% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_db_instance

Total errors: 12

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 8 | 66.67% |
| Syntax | 4 | 33.33% |

### aws_route53_record

Total errors: 11

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 11 | 100.00% |

### aws_lambda_function

Total errors: 11

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 11 | 100.00% |

### aws_kinesis_firehose_delivery_stream

Total errors: 7

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 7 | 100.00% |

### aws_connect_instance

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
