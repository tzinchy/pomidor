from repository.auth_repository import AuthRepository
from service.auth_service import AuthService
from service.auth_email_service import AuthEmailService
from repository.database import auth_session

auth_email_service = AuthEmailService() 

auth_repository = AuthRepository(auth_session)
auth_service = AuthService(auth_repository, email_service=auth_email_service)

#user_service = UserService(user_repository = user_repository,email_service = user_email_service) 

if __name__ == '__main__':
    import asyncio
    asyncio.run(auth_service.login_user('dreevxq@gmail.com', "6Nb-rp'R%m6r"))