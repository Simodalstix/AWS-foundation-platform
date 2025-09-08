from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_ssm as ssm,
    aws_iam as iam,
    Duration
)
from constructs import Construct
from typing import Dict, Any

class SlackIntegrationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, environment: str, 
                 core_resources: Dict[str, Any], alerting_resources: Dict[str, Any], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = environment
        self.core_resources = core_resources
        self.alerting_resources = alerting_resources
        self.slack_resources = {}
        
        # Single responsibility: Slack webhook function only
        self._create_slack_webhook_function()
        self._subscribe_to_alerts()
    
    def _create_slack_webhook_function(self):
        """Create Lambda function for Slack webhook integration"""
        
        # IAM role for Slack Lambda
        slack_role = iam.Role(
            self, "SlackIntegrationRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
            ],
            inline_policies={
                "SlackPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                                "kms:Decrypt"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )
        
        self.slack_resources["webhook_function"] = lambda_.Function(
            self, "SlackWebhookFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import json
import urllib3
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
http = urllib3.PoolManager()

def handler(event, context):
    try:
        # Get Slack webhook URL from SSM Parameter Store
        webhook_url = get_slack_webhook_url()
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return {'statusCode': 200, 'message': 'Slack not configured'}
        
        # Process SNS message
        for record in event.get('Records', []):
            if record.get('EventSource') == 'aws:sns':
                sns_message = json.loads(record['Sns']['Message'])
                slack_message = format_slack_message(sns_message, record['Sns'])
                send_to_slack(webhook_url, slack_message)
        
        return {'statusCode': 200, 'message': 'Messages sent to Slack'}
        
    except Exception as e:
        logger.error(f"Error sending to Slack: {str(e)}")
        return {'statusCode': 500, 'error': str(e)}

def get_slack_webhook_url():
    try:
        response = ssm.get_parameter(
            Name='/observability/dev/slack/webhook-url',
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.warning(f"Could not get Slack webhook URL: {e}")
        return None

def format_slack_message(sns_message, sns_metadata):
    # Determine alert severity from topic name
    topic_name = sns_metadata.get('TopicArn', '').split(':')[-1]
    severity = 'info'
    color = '#36a64f'  # green
    
    if 'critical' in topic_name.lower():
        severity = 'critical'
        color = '#ff0000'  # red
    elif 'high' in topic_name.lower():
        severity = 'high' 
        color = '#ff6600'  # orange
    elif 'medium' in topic_name.lower():
        severity = 'medium'
        color = '#ffcc00'  # yellow
    
    # Handle CloudWatch Alarm messages
    if 'AlarmName' in sns_message:
        return format_cloudwatch_alarm(sns_message, severity, color)
    
    # Handle custom messages
    return format_custom_message(sns_message, severity, color, sns_metadata)

def format_cloudwatch_alarm(alarm_data, severity, color):
    alarm_name = alarm_data.get('AlarmName', 'Unknown Alarm')
    new_state = alarm_data.get('NewStateValue', 'UNKNOWN')
    reason = alarm_data.get('NewStateReason', 'No reason provided')
    
    # Emoji based on state
    emoji = '🚨' if new_state == 'ALARM' else '✅' if new_state == 'OK' else '⚠️'
    
    return {
        'text': f'{emoji} CloudWatch Alert - {severity.upper()}',
        'attachments': [{
            'color': color,
            'fields': [
                {'title': 'Alarm Name', 'value': alarm_name, 'short': True},
                {'title': 'State', 'value': new_state, 'short': True},
                {'title': 'Reason', 'value': reason, 'short': False},
                {'title': 'Time', 'value': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), 'short': True}
            ]
        }]
    }

def format_custom_message(message_data, severity, color, sns_metadata):
    subject = sns_metadata.get('Subject', 'AWS Observability Alert')
    
    return {
        'text': f'🔔 {subject}',
        'attachments': [{
            'color': color,
            'fields': [
                {'title': 'Severity', 'value': severity.upper(), 'short': True},
                {'title': 'Message', 'value': str(message_data), 'short': False},
                {'title': 'Time', 'value': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'), 'short': True}
            ]
        }]
    }

def send_to_slack(webhook_url, message):
    try:
        response = http.request(
            'POST',
            webhook_url,
            body=json.dumps(message).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status != 200:
            logger.error(f"Slack API error: {response.status} - {response.data}")
        else:
            logger.info("Message sent to Slack successfully")
            
    except Exception as e:
        logger.error(f"Failed to send message to Slack: {e}")
        raise
            """),
            role=slack_role,
            timeout=Duration.minutes(1),
            tracing=lambda_.Tracing.ACTIVE,
            environment={
                "ENVIRONMENT": self.env_name
            }
        )
    
    def _subscribe_to_alerts(self):
        """Subscribe Slack function to SNS alert topics"""
        
        # Subscribe to critical and high severity alerts only
        for severity in ["critical", "high"]:
            if severity in self.alerting_resources["topics"]:
                topic = self.alerting_resources["topics"][severity]
                topic.add_subscription(
                    subscriptions.LambdaSubscription(self.slack_resources["webhook_function"])
                )