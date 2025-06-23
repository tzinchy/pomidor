from repository.old_apart_repository import OldApartRepository
from repository.new_apart_repository import NewApartRepository
from repository.dashboard_repository import DashboardRepository
from repository.database import project_managment_session
from repository.history_repository import HistoryRepository
from repository.env_repository import EnvRepository
from repository.order_repository import OrderRepository
from repository.offer_repository import OfferRepository
from repository.cin_repository import CinReposiory

from service.apart_service import ApartService
from service.dashboard_service import DashboardService
from service.history_service import HistoryService 
from service.env_service import EnvService
from service.order_service import OrderService
from service.offer_service import OfferService
from service.cin_service import CinService

old_apartment_repository = OldApartRepository(project_managment_session)
new_apartment_repository = NewApartRepository(project_managment_session)
apartment_service = ApartService(old_apart_repository=old_apartment_repository, new_apart_repositroy=new_apartment_repository)

dashboard_repository = DashboardRepository()
dashboard_service = DashboardService(dashboard_repository)

history_repository = HistoryRepository(project_managment_session)
history_service = HistoryService(history_repository)

env_repository = EnvRepository(project_managment_session)
env_service = EnvService(env_repository)

order_repository = OrderRepository(project_managment_session)
order_service = OrderService(order_repository)

offer_repository = OfferRepository(project_managment_session)
offer_service = OfferService(offer_repository)

cin_repository = CinReposiory(project_managment_session)
cin_service = CinService(cin_repository)
