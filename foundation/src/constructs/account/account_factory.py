from constructs import Construct
from aws_cdk import aws_organizations as orgs
from aws_cdk import aws_iam as iam

class AccountFactory(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)
        
        self.organization = orgs.CfnOrganization(
            self, "Organization",
            feature_set="ALL"
        )
        
        self._create_organizational_units()
        self._create_cross_account_roles()
    
    def _create_organizational_units(self):
        self.core_ou = orgs.CfnOrganizationalUnit(
            self, "CoreOU",
            name="Core",
            parent_id=self.organization.attr_root_id
        )
        
        self.security_ou = orgs.CfnOrganizationalUnit(
            self, "SecurityOU",
            name="Security",
            parent_id=self.organization.attr_root_id
        )
        
        self.workloads_ou = orgs.CfnOrganizationalUnit(
            self, "WorkloadsOU", 
            name="Workloads",
            parent_id=self.organization.attr_root_id
        )
        
        self.sandbox_ou = orgs.CfnOrganizationalUnit(
            self, "SandboxOU",
            name="Sandbox", 
            parent_id=self.organization.attr_root_id
        )
    
    def _create_cross_account_roles(self):
        self.org_admin_role = iam.Role(
            self, "OrganizationAdminRole",
            assumed_by=iam.AccountRootPrincipal(),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("OrganizationsFullAccess")
            ]
        )
    
    def create_account(self, name: str, email: str, ou_id: str) -> orgs.CfnAccount:
        return orgs.CfnAccount(
            self, f"Account{name}",
            account_name=name,
            email=email
        )