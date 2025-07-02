from neomediapi.domain.user.dtos.user_dto import UserCreateDTO
from neomediapi.domain.user.exeptions import UserAlreadyExistsError
from neomediapi.domain.user.mappers.user_mapper import map_user_create_dto_to_entity

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreateDTO, firebase_uid: str):
        existing_user = self.user_repository.get_by_firebase_uid(firebase_uid)
        if existing_user:
            raise UserAlreadyExistsError()

        user_entity = map_user_create_dto_to_entity(user_data, firebase_uid)
        return self.user_repository.save(user_entity)
