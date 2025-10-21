import logging
import streamlit as st
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceNotFoundError, AzureError, ResourceExistsError
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class AzureHandler:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.table_clients = {}  # Cache for table clients

    def _get_table_client(self, table_name: str) -> TableServiceClient:
        """Returns the table client for the given table, using a cache for reuse."""
        if table_name not in self.table_clients:
            table_service_client = TableServiceClient.from_connection_string(self.connection_string)
            self.table_clients[table_name] = table_service_client.get_table_client(table_name)
        return self.table_clients[table_name]

    def retrieve_entity(self, table_name: str, partition_key: str, row_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves an entity from the given table by partition and row key."""
        try:
            table_client = self._get_table_client(table_name)
            return table_client.get_entity(partition_key=partition_key, row_key=row_key)
        except ResourceNotFoundError:
            logger.warning(f"Entity not found in table '{table_name}' with PartitionKey: '{partition_key}' and RowKey: '{row_key}'")
            return None
        except AzureError as e:
            logger.error(f"Azure error occurred while retrieving entity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise

    def retrieve_table(self, table_name: str, partition_key: Optional[str]):
        try:
            table_client = self._get_table_client(table_name)
            return table_client.query_entities(table_name, filter="PartitionKey eq '{partition_key}'")
        except ResourceNotFoundError:
            logger.warning(f"Entity not found in table '{table_name}' with PartitionKey: '{partition_key}' and RowKey: '{row_key}'")
            return None
        except AzureError as e:
            logger.error(f"Azure error occurred while retrieving entity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise

    def retrieve_table_items(self, table_name: str, filter: Optional[str] = None):
        try:
            table_client = self._get_table_client(table_name)
            return table_client.query_entities(filter)
        except ResourceNotFoundError:
            logger.warning(f"Entity not found in table '{table_name}'")
            return None
        except AzureError as e:
            logger.error(f"Azure error occurred while retrieving entity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            raise

    def _log_success(self, operation: str, entity: Dict[str, Any]) -> None:
        """Logs success messages for insert/update operations."""
        logger.info(f"{operation} entity with PartitionKey: {entity['PartitionKey']} and RowKey: {entity['RowKey']}")

    def insert_entity(self, table_name: str, entity: Dict[str, Any]) -> None:
        """Inserts a new entity into the given table."""
        table_client = self._get_table_client(table_name)
        try:
            table_client.create_entity(entity)
            self._log_success("Inserted", entity)
        except ResourceExistsError:
            logger.warning(f"Entity already exists in table '{table_name}' with PartitionKey: {entity['PartitionKey']} and RowKey: {entity['RowKey']}")

    def update_entity(self, table_name: str, entity: Dict[str, Any]) -> None:
        """Updates an existing entity in the given table."""
        table_client = self._get_table_client(table_name)
        table_client.update_entity(entity=entity, mode=UpdateMode.MERGE)
        self._log_success("Updated", entity)

    def delete_entity(self, partition_key: str, table_name: str, row_key: str):
        table_client: TableServiceClient = self._get_table_client(table_name)
        table_client.delete_entity(partition_key=partition_key, row_key=row_key)
    
    
    def check_table_exists(self, table_name: str) -> bool:
        """Checks if a table exists in Azure Table Storage."""
        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        tables = table_service_client.list_tables()
        return any(table.name == table_name for table in tables)
    
    def create_tables(self, table_name_list):
        for name in table_name_list:
            with TableServiceClient.from_connection_string(conn_str=self.connection_string, table_name=name) as table_client:
                try:
                    print(name)
                    table_item = table_client.create_table(name)
                    print(f"Created table {table_item.table_name}!")
                except ResourceExistsError:            
                    print("Table already exists")
 
