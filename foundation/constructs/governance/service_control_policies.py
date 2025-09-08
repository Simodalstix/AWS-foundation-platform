from constructs import Construct
from aws_cdk import aws_organizations as orgs
import json

class ServiceControlPolicies(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)
        
        self._create_security_baseline_scp()
        self._create_workload_restrictions_scp()
    
    def _create_security_baseline_scp(self):
        security_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "ec2:TerminateInstances",
                        "rds:DeleteDBInstance",
                        "s3:DeleteBucket"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringNotEquals": {
                            "aws:PrincipalTag/Role": "Administrator"
                        }
                    }
                },
                {
                    "Effect": "Deny", 
                    "Action": [
                        "iam:DeleteRole",
                        "iam:DeleteUser",
                        "iam:PutRolePolicy"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringNotEquals": {
                            "aws:userid": "${aws:PrincipalTag/AdminUserId}"
                        }
                    }
                }
            ]
        }
        
        self.security_scp = orgs.CfnPolicy(
            self, "SecurityBaselineSCP",
            name="SecurityBaseline",
            description="Baseline security controls",
            type="SERVICE_CONTROL_POLICY",
            content=security_policy
        )
    
    def _create_workload_restrictions_scp(self):
        workload_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Action": [
                        "ec2:RunInstances"
                    ],
                    "Resource": "arn:aws:ec2:*:*:instance/*",
                    "Condition": {
                        "ForAllValues:StringNotEquals": {
                            "ec2:InstanceType": [
                                "t3.micro",
                                "t3.small", 
                                "t3.medium"
                            ]
                        }
                    }
                }
            ]
        }
        
        self.workload_scp = orgs.CfnPolicy(
            self, "WorkloadRestrictionsSCP",
            name="WorkloadRestrictions",
            description="Workload environment restrictions",
            type="SERVICE_CONTROL_POLICY", 
            content=workload_policy
        )