#!/usr/bin/env python3
"""
AWS Foundation Platform - Unified Landing Zone and Observability
"""
import aws_cdk as cdk
from foundation.stacks.core_stack import CoreStack
from foundation.stacks.network_stack import NetworkStack
from foundation.stacks.security_stack import SecurityStack
from observability.stacks.monitoring_stack import MonitoringStack
from connectivity.stacks.vpn_stack import VpnStack
from configuration.stacks.ssm_stack import SsmStack

app = cdk.App()

# Environment configuration
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1"
)

# Foundation stacks (landing zone)
core_stack = CoreStack(app, "Foundation-Core", env=env)
network_stack = NetworkStack(app, "Foundation-Network", env=env)
security_stack = SecurityStack(app, "Foundation-Security", env=env)

# Configuration stack (SSM)
ssm_stack = SsmStack(app, "Foundation-Configuration", env=env)

# Connectivity stack (Wireguard VPN)
vpn_stack = VpnStack(
    app, "Foundation-Connectivity", 
    vpc=network_stack.vpc,
    env=env
)

# Observability stack (monitors everything)
monitoring_stack = MonitoringStack(
    app, "Foundation-Observability",
    monitored_stacks=[core_stack, network_stack, security_stack, vpn_stack, ssm_stack],
    env=env
)

# Stack dependencies
network_stack.add_dependency(core_stack)
security_stack.add_dependency(network_stack)
vpn_stack.add_dependency(network_stack)
ssm_stack.add_dependency(core_stack)
monitoring_stack.add_dependency(security_stack)

app.synth()