from constructs import Construct
from aws_cdk import aws_guardduty as guardduty
from aws_cdk import aws_securityhub as securityhub
from aws_cdk import aws_config as config
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms

class SecurityBaseline(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)
        
        self._setup_guardduty()
        self._setup_security_hub()
        self._setup_config_rules()
        self._setup_kms()
    
    def _setup_guardduty(self):
        self.guardduty_detector = guardduty.CfnDetector(
            self, "GuardDutyDetector",
            enable=True,
            finding_publishing_frequency="FIFTEEN_MINUTES"
        )
    
    def _setup_security_hub(self):
        self.security_hub = securityhub.CfnHub(
            self, "SecurityHub",
            tags={"Environment": "Production"}
        )
    
    def _setup_config_rules(self):
        self.config_recorder = config.CfnConfigurationRecorder(
            self, "ConfigRecorder",
            name="LandingZoneRecorder",
            role_arn=self._create_config_role().role_arn,
            recording_group=config.CfnConfigurationRecorder.RecordingGroupProperty(
                all_supported=True,
                include_global_resource_types=True
            )
        )
        
        config.CfnConfigRule(
            self, "RootMfaEnabledRule",
            config_rule_name="root-mfa-enabled",
            source=config.CfnConfigRule.SourceProperty(
                owner="AWS",
                source_identifier="ROOT_MFA_ENABLED"
            )
        )
    
    def _setup_kms(self):
        self.landing_zone_key = kms.Key(
            self, "LandingZoneKey",
            description="Landing Zone master key",
            enable_key_rotation=True
        )
    
    def _create_config_role(self) -> iam.Role:
        return iam.Role(
            self, "ConfigRole",
            assumed_by=iam.ServicePrincipal("config.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/ConfigRole")
            ]
        )