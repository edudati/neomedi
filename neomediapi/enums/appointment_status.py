from enum import Enum

class AppointmentStatus(str, Enum):
    """Status do agendamento"""
    SCHEDULED = "scheduled"              # Agendado
    CONFIRMED = "confirmed"              # Confirmado
    IN_PROGRESS = "in_progress"          # Em andamento
    COMPLETED = "completed"              # Concluído
    CANCELLED = "cancelled"              # Cancelado
    NO_SHOW = "no_show"                  # Não compareceu
    RESCHEDULED = "rescheduled"          # Reagendado
    PENDING = "pending"                  # Pendente
    WAITING = "waiting"                  # Aguardando
    FINISHED = "finished"                # Finalizado 