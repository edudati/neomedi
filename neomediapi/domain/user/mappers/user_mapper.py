from neomediapi.domain.user.dtos.user_dto import UserCreateDTO
from neomediapi.infra.db.models.user_model import User

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
