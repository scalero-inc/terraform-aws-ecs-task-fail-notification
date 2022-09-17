# AWS ECS Service task fail notification module

Terraform module which sends a notification to Slack when ECS task exit with code != 0.

* When ECS task fail a lambda funtion is triggered, this lambda function sents notification to Slack.

## Usage

### ECS service associated with an Application Load Balancer (ALB)

```hcl
  source = "../../modules/ecs_task_fail_notification"

  environment   = var.environment
  slack_token   = data.aws_ssm_parameter.slack_token.value
  slack_channel = var.slack_channel

  tags = var.tags
```

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_ecs_task_fail_notification"></a> [ecs\_task\_fail\_notification](#module\_ecs\_task\_fail\_notification) | terraform-aws-modules/lambda/aws | 2.21.0 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.ecs_task_stop_event](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.ecs_task_stop_event](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_environment"></a> [environment](#input\_environment) | Environment name. | `string` | n/a | yes |
| <a name="input_logs_lines"></a> [logs\_lines](#input\_logs\_lines) | Number of lines to get from failed ECS task to show on slack message. | `string` | `"10"` | no |
| <a name="input_slack_channel"></a> [slack\_channel](#input\_slack\_channel) | Slack notification channel. | `string` | n/a | yes |
| <a name="input_slack_token"></a> [slack\_token](#input\_slack\_token) | Slack bot token | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | Additional tags (e.g. `map('BusinessUnit`,`XYZ`) | `map(string)` | `{}` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->


## Authors

Module managed by [Santiago Zurletti](https://github.com/KiddoATOM).
