from boto3 import client
from typing import Dict, List

class AccountUtils:
    def __init__(self):
        self.organizations = client('organizations')
    
    def get_account_id_by_name(self, account_name: str) -> str:
        """Get account ID by account name"""
        try:
            response = self.organizations.list_accounts()
            for account in response['Accounts']:
                if account['Name'] == account_name:
                    return account['Id']
        except Exception as e:
            print(f"Error getting account ID: {e}")
        return None
    
    def get_organizational_units(self) -> List[Dict]:
        """Get all organizational units"""
        try:
            root_id = self.organizations.list_roots()['Roots'][0]['Id']
            response = self.organizations.list_organizational_units_for_parent(ParentId=root_id)
            return response['OrganizationalUnits']
        except Exception as e:
            print(f"Error getting OUs: {e}")
        return []
    
    def validate_account_setup(self, account_id: str) -> bool:
        """Validate account baseline configuration"""
        try:
            # Check if account exists and is active
            response = self.organizations.describe_account(AccountId=account_id)
            return response['Account']['Status'] == 'ACTIVE'
        except Exception as e:
            print(f"Error validating account: {e}")
        return False