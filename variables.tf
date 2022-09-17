variable "environment" {
  type        = string
  description = "Environment name."
}

variable "logs_lines" {
  type        = string
  description = "Number of lines to get from failed ECS task to show on slack message."
  default     = "10"
}

variable "slack_token" {
  type        = string
  description = "Slack bot token"
  sensitive   = true
}

variable "slack_channel" {
  type        = string
  description = "Slack notification channel."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags (e.g. `map('BusinessUnit`,`XYZ`)"
}
