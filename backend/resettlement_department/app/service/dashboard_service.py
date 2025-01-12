from repository.dashboard_repository import DashboardRepository


class DashboardService:
    @staticmethod
    async def get_dashboard_data():
        """
        Fetches dashboard data and applies any necessary business logic.
        """
        try:
            # Fetch data from the repository
            raw_data = await DashboardRepository.get_building_details()

            return raw_data
        except Exception as e:
            print(f"Error in DashboardService: {e}")
            raise
