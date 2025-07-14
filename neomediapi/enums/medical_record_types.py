from enum import Enum

class MedicalRecordType(str, Enum):
    """Tipos de prontuário médico"""
    INITIAL_CONSULTATION = "initial_consultation"  # Consulta inicial
    FOLLOW_UP = "follow_up"                        # Acompanhamento
    EMERGENCY = "emergency"                         # Emergência
    SPECIALIST = "specialist"                       # Especialista
    THERAPY = "therapy"                             # Terapia
    EVALUATION = "evaluation"                       # Avaliação
    PRESCRIPTION = "prescription"                   # Prescrição
    LABORATORY = "laboratory"                       # Laboratório
    IMAGING = "imaging"                             # Imagem
    OTHER = "other"                                 # Outros 