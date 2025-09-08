from aws_cdk import Stack
from constructs import Construct
from src.constructs.security.security_baseline import SecurityBaseline
from src.constructs.monitoring.landing_zone_monitoring import LandingZoneMonitoring
from src.config.landing_zone_config import LandingZoneConfig

class SecurityStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: LandingZoneConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # Security baseline
        self.security_baseline = SecurityBaseline(self, "SecurityBaseline")
        
        # Monitoring and compliance
        self.monitoring = LandingZoneMonitoring(self, "Monitoring")