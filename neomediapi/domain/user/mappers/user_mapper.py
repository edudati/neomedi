from neomediapi.domain.user.dtos.user_dto import UserCreateDTO, SessionVerifyResponseDTO
from neomediapi.infra.db.models.user_model import User
from neomediapi.enums.user_roles import UserRole

def map_user_create_dto_to_entity(
    dto: UserCreateDTO,
    firebase_uid: str
) -> User:
    return User(
        name=dto.name,
        email=dto.email,
        role=dto.role,
        firebase_uid=firebase_uid,
    )


def map_user_to_session_verify_dto(
    user: User,
    email: str,
    email_verified: bool
) -> SessionVerifyResponseDTO:
    return SessionVerifyResponseDTO(
        user_id=str(user.firebase_uid),
        email=email,
        role=UserRole(user.role),
        email_verified=email_verified
    )
