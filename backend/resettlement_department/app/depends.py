from repository.apartment_repository import ApartmentRepository
from repository.dashboard_repository import DashboardRepository
from repository.database import project_managment_session
from repository.history_repository import HistoryRepository
from repository.env_repository import EnvRepository

from service.apartment_service import ApartmentService
from service.dashboard_service import DashboardService
from service.history_service import HistoryService 
from service.env_service import EnvService

apartment_repository = ApartmentRepository(project_managment_session)
apartment_service = ApartmentService(apartment_repository)

dashboard_repository = DashboardRepository()
dashboard_service = DashboardService(dashboard_repository)

history_repository = HistoryRepository(project_managment_session)
history_service = HistoryService(history_repository)

env_repository = EnvRepository(project_managment_session)
env_service = EnvService(env_repository)
