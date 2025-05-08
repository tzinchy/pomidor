from repository.user_repository import UserRepository
from service.user_service import UserService
from service.email_service import EmailService
from repository.database import auth_session

email_service = EmailService() 

user_repository = UserRepository(auth_session)
user_service = UserService(user_repository, email_service=email_service)



if __name__ == '__main__':
    import asyncio
    asyncio.run(user_service.reset_password('7ad56dd7-fba0-4298-9be8-9a52db9abb41'))