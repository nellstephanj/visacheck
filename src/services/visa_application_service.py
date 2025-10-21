"""Service layer for Visa Application management"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class VisaApplicationService:
    """Service for managing visa applications in Azure Table Storage"""
    
    def __init__(self, azure_handler, table_name: str = "VisaApplications"):
        self.azure_handler = azure_handler
        self.table_name = table_name
        
    def create_application(self, application_data: Dict[str, Any]) -> str:
        """
        Create a new visa application
        
        Args:
            application_data: Dictionary containing visa application details
            
        Returns:
            The application number (RowKey) of the created application
        """
        try:
            # Generate unique application number if not provided
            application_number = application_data.get('application_number') or str(uuid.uuid4())
            
            # Prepare entity for Azure Table Storage
            entity = {
                'PartitionKey': 'VisaApplication',
                'RowKey': application_number,
                'ApplicationNumber': application_number,
                'CaseType': application_data.get('case_type', ''),
                'VisaTypeRequested': application_data.get('visa_type_requested', ''),
                'ApplicationType': application_data.get('application_type', ''),
                'SubmissionDate': application_data.get('submission_date', ''),
                'IntakeLocation': application_data.get('intake_location', ''),
                'ApplicantIsMinor': application_data.get('applicant_is_minor', False),
                'IsUrgent': application_data.get('is_urgent', False),
                'GivenName': application_data.get('given_name', ''),
                'Surname': application_data.get('surname', ''),
                'VariationInBirthCertificate': application_data.get('variation_in_birth_certificate', False),
                'Gender': application_data.get('gender', ''),
                'CountryOfNationality': application_data.get('country_of_nationality', ''),
                'StreetNumber': application_data.get('street_number', ''),
                'UnitNumber': application_data.get('unit_number', ''),
                'PostalCode': application_data.get('postal_code', ''),
                'City': application_data.get('city', ''),
                'Country': application_data.get('country', ''),
                'DateOfBirth': application_data.get('date_of_birth', ''),
                'StateOfBirth': application_data.get('state_of_birth', ''),
                'PlaceOfBirth': application_data.get('place_of_birth', ''),
                'CountryOfBirth': application_data.get('country_of_birth', ''),
                'ResidencyStatusInAustralia': application_data.get('residency_status_in_australia', ''),
                'CivilStatus': application_data.get('civil_status', ''),
                'PackagedMemberOfEU': application_data.get('packaged_member_of_eu', False),
                'Occupation': application_data.get('occupation', ''),
                'CreatedAt': datetime.utcnow().isoformat(),
                'UpdatedAt': datetime.utcnow().isoformat(),
                'CreatedBy': application_data.get('created_by', 'system'),
                'Status': application_data.get('status', 'Draft')
            }
            
            self.azure_handler.insert_entity(self.table_name, entity)
            logger.info(f"Created visa application: {application_number}")
            return application_number
            
        except Exception as e:
            logger.error(f"Error creating visa application: {str(e)}")
            raise
    
    def get_application(self, application_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a visa application by application number
        
        Args:
            application_number: The application number (RowKey)
            
        Returns:
            Dictionary containing application details or None if not found
        """
        try:
            entity = self.azure_handler.retrieve_entity(
                self.table_name,
                'VisaApplication',
                application_number
            )
            return entity
        except Exception as e:
            logger.error(f"Error retrieving visa application: {str(e)}")
            raise
    
    def update_application(self, application_number: str, application_data: Dict[str, Any]) -> None:
        """
        Update an existing visa application
        
        Args:
            application_number: The application number (RowKey)
            application_data: Dictionary containing updated application details
        """
        try:
            # Retrieve existing entity
            existing_entity = self.get_application(application_number)
            if not existing_entity:
                raise ValueError(f"Application not found: {application_number}")
            
            # Update entity with new data
            existing_entity.update({
                'CaseType': application_data.get('case_type', existing_entity.get('CaseType')),
                'VisaTypeRequested': application_data.get('visa_type_requested', existing_entity.get('VisaTypeRequested')),
                'ApplicationType': application_data.get('application_type', existing_entity.get('ApplicationType')),
                'SubmissionDate': application_data.get('submission_date', existing_entity.get('SubmissionDate')),
                'IntakeLocation': application_data.get('intake_location', existing_entity.get('IntakeLocation')),
                'ApplicantIsMinor': application_data.get('applicant_is_minor', existing_entity.get('ApplicantIsMinor')),
                'IsUrgent': application_data.get('is_urgent', existing_entity.get('IsUrgent')),
                'GivenName': application_data.get('given_name', existing_entity.get('GivenName')),
                'Surname': application_data.get('surname', existing_entity.get('Surname')),
                'VariationInBirthCertificate': application_data.get('variation_in_birth_certificate', existing_entity.get('VariationInBirthCertificate')),
                'Gender': application_data.get('gender', existing_entity.get('Gender')),
                'CountryOfNationality': application_data.get('country_of_nationality', existing_entity.get('CountryOfNationality')),
                'StreetNumber': application_data.get('street_number', existing_entity.get('StreetNumber')),
                'UnitNumber': application_data.get('unit_number', existing_entity.get('UnitNumber')),
                'PostalCode': application_data.get('postal_code', existing_entity.get('PostalCode')),
                'City': application_data.get('city', existing_entity.get('City')),
                'Country': application_data.get('country', existing_entity.get('Country')),
                'DateOfBirth': application_data.get('date_of_birth', existing_entity.get('DateOfBirth')),
                'StateOfBirth': application_data.get('state_of_birth', existing_entity.get('StateOfBirth')),
                'PlaceOfBirth': application_data.get('place_of_birth', existing_entity.get('PlaceOfBirth')),
                'CountryOfBirth': application_data.get('country_of_birth', existing_entity.get('CountryOfBirth')),
                'ResidencyStatusInAustralia': application_data.get('residency_status_in_australia', existing_entity.get('ResidencyStatusInAustralia')),
                'CivilStatus': application_data.get('civil_status', existing_entity.get('CivilStatus')),
                'PackagedMemberOfEU': application_data.get('packaged_member_of_eu', existing_entity.get('PackagedMemberOfEU')),
                'Occupation': application_data.get('occupation', existing_entity.get('Occupation')),
                'UpdatedAt': datetime.utcnow().isoformat(),
                'Status': application_data.get('status', existing_entity.get('Status'))
            })
            
            self.azure_handler.update_entity(self.table_name, existing_entity)
            logger.info(f"Updated visa application: {application_number}")
            
        except Exception as e:
            logger.error(f"Error updating visa application: {str(e)}")
            raise
    
    def delete_application(self, application_number: str) -> None:
        """
        Delete a visa application
        
        Args:
            application_number: The application number (RowKey)
        """
        try:
            self.azure_handler.delete_entity(
                'VisaApplication',
                self.table_name,
                application_number
            )
            logger.info(f"Deleted visa application: {application_number}")
        except Exception as e:
            logger.error(f"Error deleting visa application: {str(e)}")
            raise
    
    def list_applications(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all visa applications with optional filtering
        
        Args:
            filter_query: Optional OData filter query
            
        Returns:
            List of application dictionaries
        """
        try:
            if filter_query:
                entities = self.azure_handler.retrieve_table_items(self.table_name, filter_query)
            else:
                entities = self.azure_handler.retrieve_table_items(self.table_name, "PartitionKey eq 'VisaApplication'")
            
            return list(entities) if entities else []
        except Exception as e:
            logger.error(f"Error listing visa applications: {str(e)}")
            raise
