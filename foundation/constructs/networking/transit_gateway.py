from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ram as ram

class TransitGateway(Construct):
    def __init__(self, scope: Construct, construct_id: str, asn: int = 64512, **kwargs):
        super().__init__(scope, construct_id)
        
        self.transit_gateway = ec2.CfnTransitGateway(
            self, "TransitGateway",
            amazon_side_asn=asn,
            description="Landing Zone Transit Gateway",
            default_route_table_association="enable",
            default_route_table_propagation="enable"
        )
        
        self._create_route_tables()
        self._setup_resource_sharing()
    
    def _create_route_tables(self):
        self.shared_route_table = ec2.CfnTransitGatewayRouteTable(
            self, "SharedRouteTable",
            transit_gateway_id=self.transit_gateway.ref
        )
        
        self.workload_route_table = ec2.CfnTransitGatewayRouteTable(
            self, "WorkloadRouteTable", 
            transit_gateway_id=self.transit_gateway.ref
        )
    
    def _setup_resource_sharing(self):
        from aws_cdk import Stack
        stack = Stack.of(self)
        
        self.resource_share = ram.CfnResourceShare(
            self, "TGWResourceShare",
            name="TransitGateway-Share",
            resource_arns=[
                f"arn:aws:ec2:{stack.region}:{stack.account}:transit-gateway/{self.transit_gateway.ref}"
            ],
            allow_external_principals=False
        )
    
    def attach_vpc(self, vpc_name: str, vpc_id: str, subnet_ids: list, route_table_id: str) -> ec2.CfnTransitGatewayAttachment:
        attachment = ec2.CfnTransitGatewayAttachment(
            self, f"TGWAttachment{vpc_name}",
            transit_gateway_id=self.transit_gateway.ref,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids
        )
        
        ec2.CfnTransitGatewayRouteTableAssociation(
            self, f"RTAssociation{vpc_name}",
            transit_gateway_attachment_id=attachment.ref,
            transit_gateway_route_table_id=route_table_id
        )
        
        return attachment