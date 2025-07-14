from enum import Enum

class MedicalRecordStatus(str, Enum):
    """Status do prontuário médico"""
    DRAFT = "draft"                    # Rascunho
    IN_PROGRESS = "in_progress"        # Em andamento
    COMPLETED = "completed"            # Concluído
    CANCELLED = "cancelled"            # Cancelado
    ARCHIVED = "archived"              # Arquivado
    PENDING_REVIEW = "pending_review"  # Aguardando revisão
    APPROVED = "approved"              # Aprovado
    REJECTED = "rejected"              # Rejeitado 