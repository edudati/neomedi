from typing import Optional

class AppointmentException(Exception):
    """Base exception for appointment domain"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AppointmentNotFoundError(AppointmentException):
    """Raised when appointment is not found"""
    def __init__(self, appointment_id: int):
        super().__init__(
            f"Agendamento com ID {appointment_id} não encontrado",
            "APPOINTMENT_NOT_FOUND"
        )

class AppointmentAlreadyExistsError(AppointmentException):
    """Raised when appointment already exists for the same time slot"""
    def __init__(self, professional_id: int, appointment_date: str):
        super().__init__(
            f"Já existe um agendamento para o profissional {professional_id} na data/hora {appointment_date}",
            "APPOINTMENT_ALREADY_EXISTS"
        )

class AppointmentTimeConflictError(AppointmentException):
    """Raised when appointment time conflicts with existing appointment"""
    def __init__(self, professional_id: int, appointment_date: str, duration: int):
        super().__init__(
            f"Conflito de horário para o profissional {professional_id} na data/hora {appointment_date} com duração {duration}min",
            "APPOINTMENT_TIME_CONFLICT"
        )

class AppointmentInvalidStatusTransitionError(AppointmentException):
    """Raised when trying to change appointment status to an invalid state"""
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            f"Transição de status inválida: {current_status} -> {new_status}",
            "INVALID_STATUS_TRANSITION"
        )

class AppointmentOutsideAvailabilityError(AppointmentException):
    """Raised when appointment is scheduled outside professional availability"""
    def __init__(self, professional_id: int, appointment_date: str):
        super().__init__(
            f"Agendamento fora da disponibilidade do profissional {professional_id} na data/hora {appointment_date}",
            "APPOINTMENT_OUTSIDE_AVAILABILITY"
        )

class AppointmentInvalidDurationError(AppointmentException):
    """Raised when appointment duration is invalid"""
    def __init__(self, duration: int, min_duration: int = 15, max_duration: int = 480):
        super().__init__(
            f"Duração inválida: {duration}min. Deve estar entre {min_duration} e {max_duration} minutos",
            "INVALID_DURATION"
        )

class AppointmentPastDateError(AppointmentException):
    """Raised when trying to schedule appointment in the past"""
    def __init__(self, appointment_date: str):
        super().__init__(
            f"Não é possível agendar para data/hora no passado: {appointment_date}",
            "PAST_DATE_ERROR"
        )

class AppointmentPermissionError(AppointmentException):
    """Raised when user doesn't have permission to perform action on appointment"""
    def __init__(self, action: str, appointment_id: int):
        super().__init__(
            f"Sem permissão para {action} o agendamento {appointment_id}",
            "PERMISSION_ERROR"
        )

class ProfessionalAvailabilityNotFoundError(AppointmentException):
    """Raised when professional availability is not found"""
    def __init__(self, availability_id: int):
        super().__init__(
            f"Disponibilidade com ID {availability_id} não encontrada",
            "AVAILABILITY_NOT_FOUND"
        )

class ProfessionalAvailabilityConflictError(AppointmentException):
    """Raised when professional availability conflicts with existing one"""
    def __init__(self, professional_id: int, day_of_week: int):
        super().__init__(
            f"Já existe disponibilidade para o profissional {professional_id} no dia {day_of_week}",
            "AVAILABILITY_CONFLICT"
        )

class ProfessionalAvailabilityInvalidTimeError(AppointmentException):
    """Raised when availability time is invalid"""
    def __init__(self, start_time: str, end_time: str):
        super().__init__(
            f"Horário inválido: início {start_time} deve ser anterior ao fim {end_time}",
            "INVALID_TIME_RANGE"
        )

class NoAvailableSlotsError(AppointmentException):
    """Raised when no available slots are found"""
    def __init__(self, professional_id: int, date: str):
        super().__init__(
            f"Nenhum horário disponível encontrado para o profissional {professional_id} na data {date}",
            "NO_AVAILABLE_SLOTS"
        ) 