import boto3
import json
import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from botocore.exceptions import ClientError

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)


def is_fail_event(event):
    if event['detail']['containers'][0]['exitCode'] != 0:
        if "Scaling activity initiated" in event['detail']['stoppedReason']:
            return False
        elif "container instance is in DRAINING state" in event['detail']['stoppedReason']:
            return False
        else:
            return True
    return False


def get_log_info(task_definition):
    client = boto3.client('ecs')
    response = client.describe_task_definition(
        taskDefinition=task_definition,
    )
    log_info = response['taskDefinition']['containerDefinitions'][0]['logConfiguration']

    return log_info


def get_ecs_task_log_link(event):
    task_definition = event['detail']['taskDefinitionArn'].split('/')[-1]
    container_name = event['detail']['containers'][0]['name']

    log_info = get_log_info(task_definition)

    if log_info['logDriver'] != "awslogs":
        return

    ecs_log_url = "https://{}.console.aws.amazon.com/cloudwatch/home?region={}#logsV2:log-groups/log-group/{}/log-events/{}$252F{}$252F{}".format(
        log_info['options']['awslogs-region'],
        log_info['options']['awslogs-region'],
        log_info['options']['awslogs-group'].replace("/", "$252F"),
        task_definition.split(':')[0],
        container_name,
        event['detail']['containers'][0]['taskArn'].split('/')[-1]

    )
    return ecs_log_url


def get_last_log(event):
    task_definition = event['detail']['taskDefinitionArn'].split('/')[-1]
    container_name = event['detail']['containers'][0]['name']

    log_info = get_log_info(task_definition)

    client = boto3.client('logs')
    log_stream = task_definition.split(':')[0] + "/" + container_name + "/" + event['detail']['containers'][0]['taskArn'].split('/')[-1] 
    response = client.get_log_events(
        logGroupName=log_info['options']['awslogs-group'],
        logStreamName=log_stream,
        limit=int(os.environ['LOGS_LINES']),
    )
    return [event['message'] for event in response['events']]


def lambda_handler(event, context):
    print('REQUEST RECEIVED: {}'.format(json.dumps(event, default=str)))
    if is_fail_event(event):
        print('REQUEST RECEIVED: {}'.format(json.dumps(event, default=str)))
    else:
        return

    environment = os.environ['ENVIRONMENT'].title()

    container_name = event['detail']['containers'][0]['name']
    ecs_task_log_url = get_ecs_task_log_link(event)
    last_log = get_last_log(event)
    text = "*Stop reason:* " + event['detail']['stoppedReason'] + "\n *Last log lines:*\n" + '\n'.join(last_log)

    slack_message = "[*" + environment + "*] ECS task FAIL `" + container_name + "`"
    color = "#EC0030"
    slack_attachment = [
        {
            "fallback": "Check the Cloudwatch Logs for details.",
            "color": color,
            "title": "View more Details in AWS CloudWatch Logs",
            "text": text ,
            "title_link": ecs_task_log_url,
        }
    ]

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    try:
        response = client.chat_postMessage(
            channel=os.environ['SLACK_CHANNEL'],
            text=slack_message,
            attachments=slack_attachment,
            unfurl_links=False
        )
    except SlackApiError as e:
        logger.error('Got an error: {}'.format(
            e.response['error'])
        )
    logger.info('Slack response: {}'.format(response))


