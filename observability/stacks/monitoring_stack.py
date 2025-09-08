"""Unified Monitoring Stack - Observes all platform components"""
import aws_cdk as cdk
from aws_cdk import aws_cloudwatch as cloudwatch
from constructs import Construct
from typing import List


class MonitoringStack(cdk.Stack):
    """Stack that monitors all other platform stacks"""
    
    def __init__(self, scope: Construct, construct_id: str, monitored_stacks: List[cdk.Stack], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.monitored_stacks = monitored_stacks
        
        # Create a simple dashboard for the platform
        self.dashboard = cloudwatch.Dashboard(
            self, "PlatformDashboard",
            dashboard_name="AWS-Foundation-Platform"
        )
        
        # Add basic widgets for each monitored stack
        for stack in monitored_stacks:
            self.dashboard.add_widgets(
                cloudwatch.TextWidget(
                    markdown=f"## {stack.stack_name}",
                    width=24,
                    height=1
                )
            )