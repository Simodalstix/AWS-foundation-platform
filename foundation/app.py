#!/usr/bin/env python3
from aws_cdk import App
from src.stacks.core_stack import CoreStack
from src.stacks.security_stack import SecurityStack
from src.stacks.network_stack import NetworkStack
from src.stacks.workload_stack import WorkloadStack
from src.config.landing_zone_config import LandingZoneConfig

app = App()
config = LandingZoneConfig()

core = CoreStack(app, "LandingZone-Core", config=config)
security = SecurityStack(app, "LandingZone-Security", config=config)
network = NetworkStack(app, "LandingZone-Network", config=config)
workload = WorkloadStack(app, "LandingZone-Workload", config=config)

app.synth()