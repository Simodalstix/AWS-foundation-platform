"""SSM Configuration Stack - Parameter Store and Secrets Manager"""
import aws_cdk as cdk
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class SsmStack(cdk.Stack):
    """Stack for SSM Parameter Store and configuration management"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create basic platform configuration parameters
        self.platform_config = ssm.StringParameter(
            self, "PlatformConfig",
            parameter_name="/foundation/platform/version",
            string_value="0.1.0",
            description="Platform version"
        )
        
        # Home lab network configuration
        self.lab_network = ssm.StringParameter(
            self, "LabNetwork",
            parameter_name="/foundation/connectivity/lab-network",
            string_value="192.168.198.0/24",
            description="Home lab network CIDR"
        )