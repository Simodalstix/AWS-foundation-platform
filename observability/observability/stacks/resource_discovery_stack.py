from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    Duration
)
from constructs import Construct
from typing import Dict, Any

class ResourceDiscoveryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, environment: str, core_resources: Dict[str, Any], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.env_name = environment
        self.core_resources = core_resources
        self.discovery_resources = {}
        
        # Create resource discovery components
        self._create_discovery_role()
        self._create_discovery_function()
        self._create_alarm_creator()
        self._create_discovery_scheduler()
    
    def _create_discovery_role(self):
        """Create IAM role for resource discovery with necessary permissions"""
        self.discovery_resources["role"] = iam.Role(
            self, "ResourceDiscoveryRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess")
            ],
            inline_policies={
                "ResourceDiscoveryPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "ec2:DescribeInstances",
                                "lambda:ListFunctions",
                                "rds:DescribeDBInstances",
                                "ecs:ListClusters",
                                "ecs:ListServices",
                                "cloudwatch:PutMetricAlarm",
                                "cloudwatch:DescribeAlarms",
                                "cloudwatch:DeleteAlarms"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )
    
    def _create_discovery_function(self):
        """Create Lambda function for resource discovery"""
        self.discovery_resources["discoverer"] = lambda_.Function(
            self, "ResourceDiscoverer",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        ec2 = boto3.client('ec2')
        lambda_client = boto3.client('lambda')
        rds = boto3.client('rds')
        
        # Discover resources
        resources = {
            'ec2_instances': discover_ec2_instances(ec2),
            'lambda_functions': discover_lambda_functions(lambda_client),
            'rds_instances': discover_rds_instances(rds)
        }
        
        logger.info(f"Discovered {sum(len(v) for v in resources.values())} resources")
        
        return {
            'statusCode': 200,
            'resources': resources
        }
        
    except Exception as e:
        logger.error(f"Discovery error: {str(e)}")
        return {'statusCode': 500, 'error': str(e)}

def discover_ec2_instances(ec2):
    try:
        response = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType']
                })
        return instances
    except Exception as e:
        logger.warning(f"EC2 discovery failed: {e}")
        return []

def discover_lambda_functions(lambda_client):
    try:
        response = lambda_client.list_functions()
        return [{'name': f['FunctionName']} for f in response['Functions']]
    except Exception as e:
        logger.warning(f"Lambda discovery failed: {e}")
        return []

def discover_rds_instances(rds):
    try:
        response = rds.describe_db_instances()
        return [{'id': db['DBInstanceIdentifier']} 
                for db in response['DBInstances'] 
                if db['DBInstanceStatus'] == 'available']
    except Exception as e:
        logger.warning(f"RDS discovery failed: {e}")
        return []
            """),
            role=self.discovery_resources["role"],
            timeout=Duration.minutes(3),
            tracing=lambda_.Tracing.ACTIVE
        )
    
    def _create_alarm_creator(self):
        """Create Lambda function for creating alarms based on discovered resources"""
        self.discovery_resources["alarm_creator"] = lambda_.Function(
            self, "AlarmCreator",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        cloudwatch = boto3.client('cloudwatch')
        
        # Get resources from discovery event
        resources = event.get('resources', {})
        
        alarms_created = 0
        alarms_created += create_ec2_alarms(cloudwatch, resources.get('ec2_instances', []))
        alarms_created += create_lambda_alarms(cloudwatch, resources.get('lambda_functions', []))
        
        return {
            'statusCode': 200,
            'alarms_created': alarms_created
        }
        
    except Exception as e:
        logger.error(f"Alarm creation error: {str(e)}")
        return {'statusCode': 500, 'error': str(e)}

def create_ec2_alarms(cloudwatch, instances):
    count = 0
    for instance in instances:
        try:
            cloudwatch.put_metric_alarm(
                AlarmName=f"AutoDiscovered-EC2-CPU-{instance['id']}",
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='CPUUtilization',
                Namespace='AWS/EC2',
                Period=300,
                Statistic='Average',
                Threshold=80.0,
                ActionsEnabled=True,
                AlarmDescription=f"Auto-discovered high CPU alarm for {instance['id']}",
                Dimensions=[{'Name': 'InstanceId', 'Value': instance['id']}]
            )
            count += 1
        except Exception as e:
            logger.warning(f"Failed to create alarm for {instance['id']}: {e}")
    return count

def create_lambda_alarms(cloudwatch, functions):
    count = 0
    for func in functions:
        try:
            cloudwatch.put_metric_alarm(
                AlarmName=f"AutoDiscovered-Lambda-Errors-{func['name']}",
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='Errors',
                Namespace='AWS/Lambda',
                Period=300,
                Statistic='Sum',
                Threshold=5.0,
                ActionsEnabled=True,
                AlarmDescription=f"Auto-discovered error alarm for {func['name']}",
                Dimensions=[{'Name': 'FunctionName', 'Value': func['name']}]
            )
            count += 1
        except Exception as e:
            logger.warning(f"Failed to create alarm for {func['name']}: {e}")
    return count
            """),
            role=self.discovery_resources["role"],
            timeout=Duration.minutes(5),
            tracing=lambda_.Tracing.ACTIVE
        )
    
    def _create_discovery_scheduler(self):
        """Create EventBridge rules to orchestrate discovery workflow"""
        
        # Schedule resource discovery every hour
        discovery_rule = events.Rule(
            self, "ResourceDiscoverySchedule",
            schedule=events.Schedule.rate(Duration.hours(1)),
            targets=[targets.LambdaFunction(self.discovery_resources["discoverer"])]
        )
        
        # Chain discovery → alarm creation via EventBridge
        events.Rule(
            self, "DiscoveryToAlarmCreation",
            event_pattern=events.EventPattern(
                source=["lambda"],
                detail_type=["Lambda Function Invocation Result - Success"],
                detail={
                    "responsePayload": {
                        "statusCode": [200]
                    }
                }
            ),
            targets=[targets.LambdaFunction(self.discovery_resources["alarm_creator"])]
        )