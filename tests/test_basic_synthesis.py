"""Test that basic stacks can synthesize"""
import aws_cdk as cdk
from connectivity.stacks.vpn_stack import VpnStack
from configuration.stacks.ssm_stack import SsmStack
from observability.stacks.monitoring_stack import MonitoringStack
from aws_cdk import aws_ec2 as ec2


def test_ssm_stack_synthesizes():
    """Test SSM stack can synthesize"""
    app = cdk.App()
    stack = SsmStack(app, "TestSsmStack")
    template = app.synth().get_stack_by_name("TestSsmStack").template
    
    # Check that parameters were created
    resources = template["Resources"]
    ssm_params = [r for r in resources.values() if r["Type"] == "AWS::SSM::Parameter"]
    assert len(ssm_params) == 2


def test_vpn_stack_synthesizes():
    """Test VPN stack can synthesize"""
    app = cdk.App()
    
    # Create a VPC stack first, then VPN stack
    vpc_stack = cdk.Stack(app, "VpcStack")
    vpc = ec2.Vpc(vpc_stack, "TestVpc", max_azs=2)
    stack = VpnStack(app, "TestVpnStack", vpc=vpc)
    template = app.synth().get_stack_by_name("TestVpnStack").template
    
    # Check that security group was created
    resources = template["Resources"]
    security_groups = [r for r in resources.values() if r["Type"] == "AWS::EC2::SecurityGroup"]
    assert len(security_groups) >= 1


def test_monitoring_stack_synthesizes():
    """Test monitoring stack can synthesize"""
    app = cdk.App()
    
    # Create dummy stacks to monitor
    dummy_stack = cdk.Stack(app, "DummyStack")
    stack = MonitoringStack(app, "TestMonitoringStack", monitored_stacks=[dummy_stack])
    template = app.synth().get_stack_by_name("TestMonitoringStack").template
    
    # Check that dashboard was created
    resources = template["Resources"]
    dashboards = [r for r in resources.values() if r["Type"] == "AWS::CloudWatch::Dashboard"]
    assert len(dashboards) == 1