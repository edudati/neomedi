from typing import Optional

class FacilityException(Exception):
    """Base exception for facility domain"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FacilityNotFoundError(FacilityException):
    """Raised when facility is not found"""
    def __init__(self, facility_id: int):
        super().__init__(
            f"Instalação com ID {facility_id} não encontrada",
            "FACILITY_NOT_FOUND"
        )

class FacilityAlreadyExistsError(FacilityException):
    """Raised when facility already exists with same name in company"""
    def __init__(self, name: str, company_id: int):
        super().__init__(
            f"Já existe uma instalação com o nome '{name}' na empresa {company_id}",
            "FACILITY_ALREADY_EXISTS"
        )

class FacilityPermissionError(FacilityException):
    """Raised when user doesn't have permission to perform action on facility"""
    def __init__(self, action: str, facility_id: int):
        super().__init__(
            f"Sem permissão para {action} a instalação {facility_id}",
            "PERMISSION_ERROR"
        )

class FacilityScheduleNotFoundError(FacilityException):
    """Raised when facility schedule is not found"""
    def __init__(self, schedule_id: int):
        super().__init__(
            f"Horário de instalação com ID {schedule_id} não encontrado",
            "FACILITY_SCHEDULE_NOT_FOUND"
        )

class FacilityScheduleConflictError(FacilityException):
    """Raised when facility schedule conflicts with existing one"""
    def __init__(self, facility_id: int, day_of_week: int):
        super().__init__(
            f"Já existe horário para a instalação {facility_id} no dia {day_of_week}",
            "FACILITY_SCHEDULE_CONFLICT"
        )

class FacilityScheduleInvalidTimeError(FacilityException):
    """Raised when facility schedule time is invalid"""
    def __init__(self, start_time: str, end_time: str):
        super().__init__(
            f"Horário inválido: início {start_time} deve ser anterior ao fim {end_time}",
            "INVALID_TIME_RANGE"
        )

class NoAvailableFacilitySlotsError(FacilityException):
    """Raised when no available facility slots are found"""
    def __init__(self, facility_id: int, date: str):
        super().__init__(
            f"Nenhum horário disponível encontrado para a instalação {facility_id} na data {date}",
            "NO_AVAILABLE_FACILITY_SLOTS"
        )

class FacilityOccupiedError(FacilityException):
    """Raised when facility is occupied at requested time"""
    def __init__(self, facility_id: int, appointment_date: str):
        super().__init__(
            f"Instalação {facility_id} está ocupada na data/hora {appointment_date}",
            "FACILITY_OCCUPIED"
        )

class FacilityTypeNotCompatibleError(FacilityException):
    """Raised when facility type is not compatible with appointment type"""
    def __init__(self, facility_type: str, appointment_type: str):
        super().__init__(
            f"Tipo de instalação '{facility_type}' não é compatível com tipo de agendamento '{appointment_type}'",
            "FACILITY_TYPE_NOT_COMPATIBLE"
        ) 