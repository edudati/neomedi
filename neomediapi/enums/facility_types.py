from enum import Enum

class FacilityType(str, Enum):
    """Tipos de instalação/sala"""
    CONSULTATION_ROOM = "consultation_room"    # Sala de consulta
    EXAMINATION_ROOM = "examination_room"      # Sala de exame
    PROCEDURE_ROOM = "procedure_room"          # Sala de procedimento
    THERAPY_ROOM = "therapy_room"              # Sala de terapia
    EMERGENCY_ROOM = "emergency_room"          # Sala de emergência
    LABORATORY = "laboratory"                  # Laboratório
    IMAGING_ROOM = "imaging_room"              # Sala de imagem
    WAITING_ROOM = "waiting_room"              # Sala de espera
    ADMINISTRATIVE = "administrative"          # Sala administrativa
    MEETING_ROOM = "meeting_room"              # Sala de reunião
    TELEMEDICINE = "telemedicine"              # Sala de telemedicina
    OTHER = "other"                            # Outros 