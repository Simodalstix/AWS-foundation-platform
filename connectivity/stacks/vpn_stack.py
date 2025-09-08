"""Wireguard VPN Stack - Secure tunnel from home lab to AWS"""
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VpnStack(cdk.Stack):
    """Stack for Wireguard VPN server in AWS"""
    
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.vpc = vpc
        
        # TODO: Implement Wireguard VPN server
        # For now, just create a placeholder security group
        self.vpn_security_group = ec2.SecurityGroup(
            self, "VpnSecurityGroup",
            vpc=self.vpc,
            description="Security group for Wireguard VPN",
            allow_all_outbound=True
        )
        
        # Allow Wireguard traffic (UDP 51820)
        self.vpn_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.udp(51820),
            "Wireguard VPN traffic"
        )