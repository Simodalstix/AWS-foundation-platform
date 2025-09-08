from aws_cdk import Stack
from constructs import Construct
from src.constructs.account.account_factory import AccountFactory
from src.constructs.governance.service_control_policies import ServiceControlPolicies
from src.config.landing_zone_config import LandingZoneConfig

class CoreStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: LandingZoneConfig, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # Organization setup
        self.account_factory = AccountFactory(self, "AccountFactory")
        
        # Governance policies
        self.scps = ServiceControlPolicies(self, "ServiceControlPolicies")
        
        # Create core accounts
        self._create_core_accounts()
    
    def _create_core_accounts(self):
        self.core_accounts = {}
        self.security_accounts = {}
        
        # Core infrastructure accounts (Core OU)
        for account_name, email in self.config.core_accounts.items():
            account = self.account_factory.create_account(
                name=account_name,
                email=email,
                ou_id=self.account_factory.core_ou.ref
            )
            self.core_accounts[account_name] = account
            
        # Security service accounts (Security OU)
        for account_name, email in self.config.security_accounts.items():
            account = self.account_factory.create_account(
                name=account_name,
                email=email,
                ou_id=self.account_factory.security_ou.ref
            )
            self.security_accounts[account_name] = account