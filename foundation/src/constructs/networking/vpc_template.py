from constructs import Construct
from aws_cdk import aws_ec2 as ec2

class VpcTemplate(Construct):
    VALID_WORKLOAD_TYPES = {"standard", "web", "database"}
    
    def __init__(self, scope: Construct, construct_id: str, cidr: str, workload_type: str = "standard", **kwargs):
        super().__init__(scope, construct_id)
        
        # Validate workload type against allowed values
        if workload_type not in self.VALID_WORKLOAD_TYPES:
            raise ValueError(f"Invalid workload_type: {workload_type}. Must be one of {self.VALID_WORKLOAD_TYPES}")
        
        self.vpc = ec2.Vpc(
            self, "VPC",
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            max_azs=3,
            subnet_configuration=self._get_subnet_config(workload_type),
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
        
        self._setup_security_groups()
        self._setup_nacls()
    
    def _get_subnet_config(self, workload_type: str) -> list:
        if workload_type == "web":
            return [
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        else:
            return [
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
    
    def _setup_security_groups(self):
        self.default_sg = ec2.SecurityGroup(
            self, "DefaultSG",
            vpc=self.vpc,
            description="Default security group with minimal access",
            allow_all_outbound=False
        )
        
        self.default_sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="HTTPS outbound"
        )
    
    def _setup_nacls(self):
        self.private_nacl = ec2.NetworkAcl(
            self, "PrivateNACL",
            vpc=self.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            )
        )