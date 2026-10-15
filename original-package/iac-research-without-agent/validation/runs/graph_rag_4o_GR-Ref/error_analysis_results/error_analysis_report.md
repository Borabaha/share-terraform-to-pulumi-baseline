# Infrastructure as Code Error Analysis Report

## Overall Statistics

- **Total Scripts Analyzed**: 458
- **Successful Scripts**: 277 (60.48%)
- **Failed Scripts**: 181 (39.52%)

## Error Count Statistics (Excluding OPA Validation Errors)

- **Total Individual Errors**: 140
- **Average Errors per Failed Script (Init/Plan)**: 1.56
- **Median Errors per Failed Script (Init/Plan)**: 1.00
- **Maximum Errors in a Script (Init/Plan)**: 8

### Error Count Distribution (Init/Plan Failures)

| Number of Errors | Number of Scripts | Percentage |
|-----------------|------------------|------------|
| 1 | 65 | 72.22% |
| 2 | 12 | 13.33% |
| 3 | 8 | 8.89% |
| 4 | 3 | 3.33% |
| 7 | 1 | 1.11% |
| 8 | 1 | 1.11% |

## Failure Distribution by Stage

| Stage | Count | Percentage |
|-------|-------|------------|
| OPA | 91 | 19.87% |
| Plan | 85 | 18.56% |
| Init | 5 | 1.09% |

## Error Categories (Excluding OPA Validation)

This section includes all errors identified across Init and Plan stages.

| Category | Count | Percentage of All Errors |
|----------|-------|-------------------------|
| Schema | 108 | 77.14% |
| Runtime | 18 | 12.86% |
| Syntax | 7 | 5.00% |
| Other | 7 | 5.00% |

## Top Error Subcategories (Excluding OPA Validation)

| Subcategory | Count | Percentage of All Errors |
|-------------|-------|-------------------------|
| Unsupported Argument | 43 | 30.71% |
| File Not Found | 15 | 10.71% |
| Missing Required Argument | 15 | 10.71% |
| Invalid Resource Reference | 11 | 7.86% |
| Unsupported Block | 10 | 7.14% |
| Format Constraint | 7 | 5.00% |
| Unclassified | 7 | 5.00% |
| Insufficient Required Blocks | 5 | 3.57% |
| Invalid Argument | 5 | 3.57% |
| Unsupported Resource | 5 | 3.57% |
| Resource: aws_elasticache_user | 3 | 2.14% |
| Version Constraint | 3 | 2.14% |
| Invalid Attribute | 3 | 2.14% |
| Resource: aws_route53_health_check | 2 | 1.43% |
| Unsupported Attribute | 2 | 1.43% |

## Most Common Resource Types with Errors

| Resource Type | Count | Percentage of Resource Errors |
|--------------|-------|------------------------------|
| aws_db_instance | 16 | 13.45% |
| aws_lambda_function | 9 | 7.56% |
| aws_network_acl_rule | 8 | 6.72% |
| aws_lex_bot | 6 | 5.04% |
| aws_mskconnect_custom_plugin | 6 | 5.04% |
| aws_route53_record | 4 | 3.36% |
| aws_kinesis_firehose_delivery_stream | 4 | 3.36% |
| aws_security_group | 4 | 3.36% |
| aws_s3_bucket_inventory | 4 | 3.36% |
| aws_vpc | 4 | 3.36% |

## Detailed Analysis by Stage

### Init Stage Failures

- **Total Scripts with Failures**: 5 (1.09% of all scripts)
- **Average Errors per Failed Script**: 2.00
- **Total Distinct Errors**: 10

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Other | 5 | 50.00% |
| Runtime | 3 | 30.00% |
| Schema | 2 | 20.00% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unclassified | 5 | 50.00% |
| Version Constraint | 3 | 30.00% |
| Unsupported Block | 2 | 20.00% |

### Plan Stage Failures

- **Total Scripts with Failures**: 85 (18.56% of all scripts)
- **Average Errors per Failed Script**: 1.53
- **Total Distinct Errors**: 130

#### Top Error Categories

| Category | Count | Percentage within Stage |
|----------|-------|-------------------------|
| Schema | 106 | 81.54% |
| Runtime | 15 | 11.54% |
| Syntax | 7 | 5.38% |
| Other | 2 | 1.54% |

#### Top Error Subcategories

| Subcategory | Count | Percentage within Stage |
|-------------|-------|-------------------------|
| Unsupported Argument | 43 | 33.08% |
| File Not Found | 15 | 11.54% |
| Missing Required Argument | 15 | 11.54% |
| Invalid Resource Reference | 11 | 8.46% |
| Unsupported Block | 8 | 6.15% |
| Format Constraint | 7 | 5.38% |
| Insufficient Required Blocks | 5 | 3.85% |
| Invalid Argument | 5 | 3.85% |
| Unsupported Resource | 5 | 3.85% |
| Resource: aws_elasticache_user | 3 | 2.31% |

### OPA Stage Failures

- **Total Scripts with Failures**: 91 (19.87% of all scripts)
- **OPA Validation Failures**: These are intent validation errors that will be analyzed separately.

## OPA Validation Results

OPA validation failures indicate cases where the script was syntactically correct but did not meet the intended requirements. These are excluded from the general error statistics above and should be analyzed separately.

- **Total OPA Validation Failures**: 91 (19.87% of all scripts)

## Resource-Specific Error Patterns

This section shows the most common error categories for each resource type.

### aws_db_instance

Total errors: 16

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 11 | 68.75% |
| Syntax | 5 | 31.25% |

### aws_lambda_function

Total errors: 9

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Runtime | 9 | 100.00% |

### aws_network_acl_rule

Total errors: 8

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 8 | 100.00% |

### aws_lex_bot

Total errors: 6

| Error Category | Count | Percentage |
|---------------|-------|------------|
| Schema | 6 | 100.00% |

### aws_mskconnect_custom_plugin

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
