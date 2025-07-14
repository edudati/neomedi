from neomediapi.infra.db.models.company_model import Company
from neomediapi.domain.company.dtos.company_dto import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyWithRelations
from neomediapi.domain.address.mappers.address_mapper import AddressMapper
from neomediapi.domain.user.mappers.user_mapper import UserMapper

class CompanyMapper:
    @staticmethod
    def to_entity(company_create: CompanyCreate, admin_user_id: int) -> Company:
        """Convert CompanyCreate DTO to Company entity"""
        return Company(
            name=company_create.name,
            trade_name=company_create.trade_name,
            cnpj=company_create.cnpj,
            corporate_name=company_create.corporate_name,
            phone_number=company_create.phone_number,
            email=company_create.email,
            website=str(company_create.website) if company_create.website else None,
            admin_user_id=admin_user_id,
            address_id=company_create.address_id
        )
    
    @staticmethod
    def to_response(company: Company) -> CompanyResponse:
        """Convert Company entity to CompanyResponse DTO"""
        return CompanyResponse(
            id=company.id,
            name=company.name,
            trade_name=company.trade_name,
            cnpj=company.cnpj,
            corporate_name=company.corporate_name,
            phone_number=company.phone_number,
            email=company.email,
            website=company.website,
            admin_user_id=company.admin_user_id,
            address_id=company.address_id,
            is_active=company.is_active,
            is_deleted=company.is_deleted,
            created_at=company.created_at,
            updated_at=company.updated_at
        )
    
    @staticmethod
    def to_response_with_relations(company: Company) -> CompanyWithRelations:
        """Convert Company entity to CompanyWithRelations DTO"""
        response = CompanyMapper.to_response(company)
        
        # Add address if available
        address_response = None
        if company.address:
            address_response = AddressMapper.to_response(company.address)
        
        # Add admin user if available
        admin_user_response = None
        if company.admin_user:
            admin_user_response = UserMapper.to_response(company.admin_user)
        
        return CompanyWithRelations(
            **response.dict(),
            address=address_response,
            admin_user=admin_user_response
        )
    
    @staticmethod
    def update_entity(company: Company, company_update: CompanyUpdate) -> Company:
        """Update Company entity with CompanyUpdate DTO"""
        update_data = company_update.dict(exclude_unset=True)
        
        # Handle website field conversion
        if 'website' in update_data and update_data['website']:
            update_data['website'] = str(update_data['website'])
        
        for field, value in update_data.items():
            if hasattr(company, field):
                setattr(company, field, value)
        
        return company 