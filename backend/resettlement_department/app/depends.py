from repository.apartment_repository import ApartmentRepository
from repository.dashboard_repository import DashboardRepository
from repository.database import project_managment_session


from service.alghorithm import match_new_apart_to_family_batch
from service.balance_alghorithm import save_views_to_excel
from service.validation_service import ValidationService
from service.apartment_insert import new_apart_insert, insert_offer, insert_data_to_structure, insert_data_to_needs
from service.apartment_service import ApartmentService
from service.dashboard_service import DashboardService


apartment_repository = ApartmentRepository(project_managment_session)
apartment_service = ApartmentService(apartment_repository)

dashboard_repository = DashboardRepository()
dashboard_service = DashboardService(dashboard_repository)

validation_service = ValidationService()

