from neomediapi.domain.user.dtos.user_dto import UserCreateDTO, SessionVerifyResponseDTO
from neomediapi.domain.user.exeptions import UserAlreadyExistsError, UserNotFoundError
from neomediapi.domain.user.mappers.user_mapper import map_user_create_dto_to_entity, map_user_to_session_verify_dto
from neomediapi.infra.db.models.user_model import User

class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreateDTO, firebase_uid: str):
        existing_user = self.user_repository.get_by_firebase_uid(firebase_uid)
        if existing_user:
            raise UserAlreadyExistsError()

        user_entity = map_user_create_dto_to_entity(user_data, firebase_uid)
        return self.user_repository.save(user_entity)

    def get_user_by_firebase_uid(self, firebase_uid: str) -> User:
        print(f"🔍 UserService: Buscando usuário por firebase_uid: {firebase_uid}")
        user = self.user_repository.get_by_firebase_uid(firebase_uid)
        if not user:
            print(f"❌ UserService: Usuário não encontrado no repositório")
            raise UserNotFoundError()
        print(f"✅ UserService: Usuário encontrado - ID: {user.id}, Role: {user.role}")
        return user

    def get_session_verify_data(self, firebase_uid: str, email: str, email_verified: bool) -> SessionVerifyResponseDTO:
        print(f"🔍 UserService: Iniciando get_session_verify_data para {firebase_uid}")
        user = self.get_user_by_firebase_uid(firebase_uid)
        session_data = map_user_to_session_verify_dto(user, email, email_verified)
        print(f"✅ UserService: Dados da sessão mapeados com sucesso")
        return session_data
