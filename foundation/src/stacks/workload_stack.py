from aws_cdk import Stack
from constructs import Construct
from src.constructs.networking.vpc_template import VpcTemplate
from src.config.landing_zone_config import LandingZoneConfig

class WorkloadStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: LandingZoneConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        self.workload_vpcs = {}
        
        # Create VPCs for each workload environment
        for env_name, cidr in config.vpc_cidr_blocks.items():
            if env_name != "shared":
                vpc = VpcTemplate(
                    self, f"{env_name.title()}VPC",
                    cidr=cidr,
                    workload_type="web" if env_name == "prod" else "standard"
                )
                self.workload_vpcs[env_name] = vpc