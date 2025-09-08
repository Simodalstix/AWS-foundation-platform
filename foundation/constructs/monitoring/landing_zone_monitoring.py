from constructs import Construct
from aws_cdk import aws_cloudtrail as cloudtrail
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_budgets as budgets
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import Duration

class LandingZoneMonitoring(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)
        
        self._setup_cloudtrail()
        self._setup_budgets()
        self._setup_dashboards()
    
    def _setup_cloudtrail(self):
        self.trail_bucket = s3.Bucket(
            self, "CloudTrailBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            enforce_ssl=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="CloudTrailLogRetention",
                    enabled=True,
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ],
                    expiration=Duration.days(2555)  # 7 years retention
                )
            ]
        )
        
        self.organization_trail = cloudtrail.Trail(
            self, "OrganizationTrail",
            bucket=self.trail_bucket,
            is_organization_trail=True,
            include_global_service_events=True,
            is_multi_region_trail=True,
            enable_file_validation=True
        )
    
    def _setup_budgets(self):
        budgets.CfnBudget(
            self, "AccountBudget",
            budget=budgets.CfnBudget.BudgetDataProperty(
                budget_name="Account-Monthly-Budget",
                budget_limit=budgets.CfnBudget.SpendProperty(
                    amount=1000,
                    unit="USD"
                ),
                time_unit="MONTHLY",
                budget_type="COST"
            ),
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        notification_type="ACTUAL",
                        comparison_operator="GREATER_THAN",
                        threshold=80
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            subscription_type="EMAIL",
                            address="admin@company.com"
                        )
                    ]
                )
            ]
        )
    
    def _setup_dashboards(self):
        self.landing_zone_dashboard = cloudwatch.Dashboard(
            self, "LandingZoneDashboard",
            dashboard_name="LandingZone-Overview"
        )
        
        self.landing_zone_dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Account Activity",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/CloudTrail",
                        metric_name="EventCount"
                    )
                ]
            )
        )