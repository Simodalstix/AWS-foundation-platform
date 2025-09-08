from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam

class BedrockModule(Construct):
    """AI/ML module for Bedrock integration with Landing Zone"""
    
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, construct_id)
        
        self._setup_bedrock_endpoints(vpc)
        self._setup_ai_governance()
        self._setup_model_access_roles()
    
    def _setup_bedrock_endpoints(self, vpc: ec2.Vpc):
        """Private Bedrock access via VPC endpoints"""
        self.bedrock_endpoint = ec2.InterfaceVpcEndpoint(
            self, "BedrockEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME,
            private_dns_enabled=True
        )
    
    def _setup_ai_governance(self):
        """AI-specific governance policies"""
        self.ai_policy = iam.ManagedPolicy(
            self, "AIGovernancePolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["bedrock:InvokeModel"],
                    resources=["*"],
                    conditions={
                        "StringEquals": {
                            "bedrock:modelId": [
                                "anthropic.claude-v2",
                                "amazon.titan-text-express-v1"
                            ]
                        }
                    }
                )
            ]
        )
    
    def _setup_model_access_roles(self):
        """Environment-specific model access"""
        self.dev_ai_role = iam.Role(
            self, "DevAIRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[self.ai_policy]
        )