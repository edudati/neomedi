from enum import Enum

class AppointmentType(str, Enum):
    """Tipos de agendamento"""
    CONSULTATION = "consultation"        # Consulta
    FOLLOW_UP = "follow_up"              # Retorno
    EMERGENCY = "emergency"              # Emergência
    EVALUATION = "evaluation"            # Avaliação
    THERAPY = "therapy"                  # Terapia
    PROCEDURE = "procedure"              # Procedimento
    EXAMINATION = "examination"          # Exame
    COUNSELING = "counseling"            # Aconselhamento
    TELEMEDICINE = "telemedicine"        # Telemedicina
    OTHER = "other"                      # Outros 