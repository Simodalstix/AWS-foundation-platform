from aws_cdk import Stack
from constructs import Construct
from src.constructs.networking.transit_gateway import TransitGateway
from src.constructs.networking.vpc_template import VpcTemplate
from src.config.landing_zone_config import LandingZoneConfig

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: LandingZoneConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # Transit Gateway for hub-and-spoke
        self.transit_gateway = TransitGateway(
            self, "TransitGateway",
            asn=config.transit_gateway_asn
        )
        
        # Shared services VPC
        self.shared_vpc = VpcTemplate(
            self, "SharedVPC",
            cidr=config.vpc_cidr_blocks["shared"],
            workload_type="standard"
        )
        
        # Attach shared VPC to Transit Gateway
        self.transit_gateway.attach_vpc(
            vpc_name="Shared",
            vpc_id=self.shared_vpc.vpc.vpc_id,
            subnet_ids=[subnet.subnet_id for subnet in self.shared_vpc.vpc.private_subnets],
            route_table_id=self.transit_gateway.shared_route_table.ref
        )