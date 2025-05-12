from repository.auth_repository import AuthRepository
from service.auth_service import AuthService
from service.auth_email_service import AuthEmailService
from repository.database import auth_session

auth_email_service = AuthEmailService() 

auth_repository = AuthRepository(auth_session)
auth_service = AuthService(auth_repository, email_service=auth_email_service)
