data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_cloudwatch_event_rule" "ecs_task_stop_event" {
  name        = "ecs_task_status_stopped"
  description = "Capture each ECS task status change"

  event_pattern = <<PATTERN
{
  "source": [
    "aws.ecs"
  ],
  "detail-type": [
    "ECS Task State Change"
  ],
  "detail": {
    "lastStatus": [
      "STOPPED"
    ]
  }
}
PATTERN
}


resource "aws_cloudwatch_event_target" "ecs_task_stop_event" {
  rule = aws_cloudwatch_event_rule.ecs_task_stop_event.name
  arn  = module.ecs_task_fail_notification.lambda_function_arn
}

module "ecs_task_fail_notification" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "ecs_task_fail_notification"
  description   = "Function that filters ECS task stop events, filter the not expected events and send slack notification."
  handler       = "ecs_task_fail_notifier.lambda_handler"
  runtime       = "python3.11"
  timeout       = 15

  source_path = "${path.module}/src"

  environment_variables = {
    SLACK_CHANNEL   = var.slack_channel
    SLACK_BOT_TOKEN = var.slack_token
    ENVIRONMENT     = var.environment
    LOGS_LINES      = var.logs_lines
  }

  allowed_triggers = {
    InstanceEvent = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.ecs_task_stop_event.arn
    }
  }

  publish = true

  attach_policy_statements = true
  policy_statements = {
    describe_task = {
      actions   = ["ecs:DescribeTaskDefinition", ]
      resources = ["*"]
      effect    = "Allow"
    }

    get_task_logs = {
      actions   = ["logs:GetLogEvents", ]
      resources = ["*"]
      effect    = "Allow"
    }
  }

  tags = merge(
    { Name = "ecs_task_fail_notification" },
    var.tags
  )
}
