from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from neomediapi.infra.db.models.company_model import Company
from neomediapi.domain.company.exceptions import CompanyNotFoundError, CompanyAlreadyExistsError

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, company: Company) -> Company:
        """Create a new company"""
        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
                raise CompanyAlreadyExistsError(f"Company with CNPJ {company.cnpj} already exists")
            raise e
    
    def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(
            and_(
                Company.id == company_id,
                Company.is_deleted.is_(False)
            )
        ).first()
    
    def get_by_admin_user_id(self, admin_user_id: int) -> Optional[Company]:
        """Get company by admin user ID"""
        return self.db.query(Company).filter(
            and_(
                Company.admin_user_id == admin_user_id,
                Company.is_deleted.is_(False)
            )
        ).first()
    
    def get_by_cnpj(self, cnpj: str) -> Optional[Company]:
        """Get company by CNPJ"""
        return self.db.query(Company).filter(
            and_(
                Company.cnpj == cnpj,
                Company.is_deleted.is_(False)
            )
        ).first()
    
    def get_all_active(self) -> List[Company]:
        """Get all active companies"""
        return self.db.query(Company).filter(
            and_(
                Company.is_active.is_(True),
                Company.is_deleted.is_(False)
            )
        ).all()
    
    def get_all(self) -> List[Company]:
        """Get all companies (including inactive but not deleted)"""
        return self.db.query(Company).filter(
            Company.is_deleted.is_(False)
        ).all()
    
    def update(self, company: Company) -> Company:
        """Update company"""
        try:
            self.db.commit()
            self.db.refresh(company)
            return company
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete(self, company: Company) -> None:
        """Soft delete company"""
        company.soft_delete()
        self.db.commit()
    
    def restore(self, company: Company) -> Company:
        """Restore soft deleted company"""
        company.restore()
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def deactivate(self, company: Company) -> Company:
        """Deactivate company"""
        company.deactivate()
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def activate(self, company: Company) -> Company:
        """Activate company"""
        company.activate()
        self.db.commit()
        self.db.refresh(company)
        return company
    
    def exists_by_cnpj(self, cnpj: str, exclude_id: Optional[int] = None) -> bool:
        """Check if company exists by CNPJ"""
        query = self.db.query(Company).filter(
            and_(
                Company.cnpj == cnpj,
                Company.is_deleted == False
            )
        )
        
        if exclude_id:
            query = query.filter(Company.id != exclude_id)
        
        return query.first() is not None
    
    def exists_by_admin_user_id(self, admin_user_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if company exists by admin user ID"""
        query = self.db.query(Company).filter(
            and_(
                Company.admin_user_id == admin_user_id,
                Company.is_deleted == False
            )
        )
        
        if exclude_id:
            query = query.filter(Company.id != exclude_id)
        
        return query.first() is not None
    
    def get_users_by_company_id(self, company_id: int) -> List:
        """Get all users in a company"""
        from neomediapi.infra.db.models.user_model import User
        return self.db.query(User).filter(
            and_(
                User.company_id == company_id,
                User.is_deleted.is_(False)
            )
        ).all()
    
    def get_users_by_company_id_and_profile(self, company_id: int, profile: str) -> List:
        """Get users in a company by profile"""
        from neomediapi.infra.db.models.user_model import User
        return self.db.query(User).filter(
            and_(
                User.company_id == company_id,
                User.profile == profile,
                User.is_deleted.is_(False)
            )
        ).all()
    
    def get_active_professionals_by_company_id(self, company_id: int) -> List:
        """Get active professionals in a company"""
        from neomediapi.infra.db.models.user_model import User
        from neomediapi.enums.user_profiles import UserProfile
        return self.db.query(User).filter(
            and_(
                User.company_id == company_id,
                User.profile == UserProfile.PROFESSIONAL,
                User.is_active.is_(True),
                User.is_deleted.is_(False)
            )
        ).all() 