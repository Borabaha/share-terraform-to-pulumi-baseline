# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 286 (62.45%)
- **Failed Scripts**: 172 (37.55%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 128
- **Average Errors per Failed Script (Init/Plan)**: 1.78
- **Median Errors per Failed Script (Init/Plan)**: 1.00
- **Maximum Errors in a Script (Init/Plan)**: 7

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 43 | 59.72% |
| 2 | 17 | 23.61% |
| 3 | 5 | 6.94% |
| 4 | 4 | 5.56% |
| 6 | 1 | 1.39% |
| 7 | 2 | 2.78% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| OPA | 100 | 21.83% |
| Plan | 69 | 15.07% |
| Init | 3 | 0.66% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 110 | 85.94% |
| Runtime | 13 | 10.16% |
| Syntax | 4 | 3.12% |
| Other | 1 | 0.78% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 34 | 26.56% |
| Missing Required Argument | 27 | 21.09% |
| Unsupported Block | 13 | 10.16% |
| File Not Found | 12 | 9.38% |
| Unsupported Attribute | 6 | 4.69% |
| Invalid Resource Reference | 6 | 4.69% |
| Invalid Argument | 5 | 3.91% |
| Duplicate Argument | 4 | 3.12% |
| Format Constraint | 4 | 3.12% |
| Insufficient Required Blocks | 4 | 3.12% |
| Resource: aws_elasticache_user | 3 | 2.34% |
| Resource: aws_eip | 3 | 2.34% |
| Unsupported Resource | 2 | 1.56% |
| Unclassified | 1 | 0.78% |
| Resource: aws_redshift_cluster | 1 | 0.78% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_route53_record | 15 | 12.20% |
| aws_db_instance | 14 | 11.38% |
| aws_lambda_function | 10 | 8.13% |
| aws_lex_bot | 7 | 5.69% |
| aws_kinesis_firehose_delivery_stream | 6 | 4.88% |
| aws_security_group | 6 | 4.88% |
| aws_connect_instance | 4 | 3.25% |
| aws_sagemaker_domain | 4 | 3.25% |
| aws_s3_bucket_inventory | 4 | 3.25% |
| aws_vpc | 4 | 3.25% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 3 (0.66% of all scripts)
- **Average Errors per Failed Script**: 2.33
- **Total Distinct Errors**: 7

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 6 | 85.71% |
| Runtime | 1 | 14.29% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Duplicate Argument | 4 | 57.14% |
| Invalid Resource Reference | 2 | 28.57% |
| Version Constraint | 1 | 14.29% |

### Plan Stage Failures

- **Total Scripts with Failures**: 69 (15.07% of all scripts)
- **Average Errors per Failed Script**: 1.75
- **Total Distinct Errors**: 121

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 104 | 85.95% |
| Runtime | 12 | 9.92% |
| Syntax | 4 | 3.31% |
| Other | 1 | 0.83% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 34 | 28.10% |
| Missing Required Argument | 27 | 22.31% |
| Unsupported Block | 13 | 10.74% |
| File Not Found | 12 | 9.92% |
| Unsupported Attribute | 6 | 4.96% |
| Invalid Argument | 5 | 4.13% |
| Format Constraint | 4 | 3.31% |
| Invalid Resource Reference | 4 | 3.31% |
| Insufficient Required Blocks | 4 | 3.31% |
| Resource: aws_elasticache_user | 3 | 2.48% |

### OPA Stage Failures

- **Total Scripts with Failures**: 100 (21.83% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 100 (21.83% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_route53_record

Total errors: 15

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 15 | 100.00% |

### aws_db_instance

Total errors: 14

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 11 | 78.57% |
| Syntax | 3 | 21.43% |

### aws_lambda_function

Total errors: 10

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 10 | 100.00% |

### aws_lex_bot

Total errors: 7

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 7 | 100.00% |

### aws_kinesis_firehose_delivery_stream

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
