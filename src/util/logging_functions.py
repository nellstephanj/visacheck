import streamlit as st
from datetime import datetime, timezone
from util.azure_functions import AzureHandler

class LoggingHandler():
    def __init__(self, azure_handler: AzureHandler, table_name: str = "UsageLogs"):
        self.azure_handler = azure_handler
        self.table_name = table_name

    def log_usage(self, model_name, log_usage_amount, log_usage_unit):
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds')

        log_entity = {
            "PartitionKey": st.session_state['user_engagement'],
            "RowKey": timestamp,
            "UserName": st.session_state['user'],
            "ModelName": model_name, 
            "UsageAmount": log_usage_amount,
            "UsageUnit": log_usage_unit
        }

        self.azure_handler.insert_entity(self.table_name, log_entity)