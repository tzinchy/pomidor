from datetime import datetime

from repository.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, repository : DashboardRepository):
        self.db = repository

    def get_tables_data(self):
        """
        Fetches dashboard data and applies any necessary business logic.
        """
        try:
            # Fetch data from the repository
            tables_data = self.db.get_tables_data()
            return tables_data
        except Exception as e:
            print(f"Error in DashboardService: {e}")
            raise

    def get_dashboard_data(self):
        dashboard_data = self.db.get_dashboard_details()
        categories = {
        "done": {},
        "fullInProgress": {"risk": {}, "noRisk": {}},
        "halfInProgress": {},
        "notStarted": {}
        }

        for new_building_id, _, _, _,  old_buildings in dashboard_data:
            all_done = True
            all_started = True
            all_actual_none = True
            risk = False
            all_dates = []
            min_date = None

            for old_building_id, details in old_buildings.items():
                f1 = details.get("f5", {})
                f2 = details.get("f2", {})
                done_date = f1.get("doneDate")
                actual_start = f1.get("actual", {}).get("firstResetlementStart")

                if done_date is None:
                    all_done = False
                if actual_start is not None:
                    any_started = True
                    all_actual_none = False
                    # Calculate difference in months
                    actual_start_date = datetime.strptime(actual_start, '%Y-%m-%d')
                    all_dates.append(actual_start_date)
                    if min_date is None or actual_start_date > min_date:
                        min_date = actual_start_date
                    
                else:
                    all_started = False

                if f2 and "Наступили риски" in f2:
                    risk = True

            if all_done:
                categories['done'][new_building_id] = list(old_buildings.keys())
            elif all_started and not all_done:
                now = datetime.now()
                date_diff_months = int((now-min_date).days / 30)
                sub_category = 'risk' if risk else 'noRisk'
                categories['fullInProgress'][sub_category][new_building_id] = {
                    "buildings": list(old_buildings.keys()),
                    "date": date_diff_months,
                    "all_dates":all_dates,
                    "min_date":min_date
                }
            elif all_actual_none:
                categories['notStarted'][new_building_id] = list(old_buildings.keys())
            elif any_started:
                categories['halfInProgress'][new_building_id] = list(old_buildings.keys())

        data1 = categories['fullInProgress']


        # Категории времени
        categories1 = ["Менее месяца", "От 1 до 2 месяцев", "От 2 до 5 месяцев", "От 5 до 8 месяцев", "Более 8 месяцев"]
        category_limits = [0, 1, 2, 5, 8, float('inf')]

        # Инициализация подсчётов
        counts = {key: [0] * len(categories1) for key in data1.keys()}

        # Подсчёт зданий в категориях
        for risk_type, buildings in data1.items():
            for building_id, details in buildings.items():
                # Проверяем, является ли details словарём
                if isinstance(details, dict) and 'date' in details:
                    months = details['date']
                else:
                    raise ValueError(f"Unexpected data format for building {building_id}: {details}")

                for i, (low, high) in enumerate(zip(category_limits[:-1], category_limits[1:])):
                    if low <= months < high:
                        counts[risk_type][i] += 1
                        break

        # Подготовка данных для диаграммы
        chart_data = {
            "categories": categories1,
            "risk_counts": counts['risk'],
            "noRisk_counts": counts['noRisk']
        }    

        data = [categories, chart_data]

        chart_data = data[1]

        done = {
            'value': len(data[0]["done"]),
            'link': '/table_page?otsel_type=%D0%9E%D1%81%D0%B2%D0%BE%D0%B1%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D1%8B',
            'color': 'text-emerald-600',
            'name': 'Освобождены',
            'svg': 'done'
        }
        halfInProgress = {
            'value': len(data[0]['halfInProgress']),
            'link': '/table_page?otsel_type=%D0%98%D0%B4%D1%91%D1%82+%D1%87%D0%B0%D1%81%D1%82%D0%B8%D1%87%D0%BD%D0%BE%D0%B5+%D0%BE%D1%81%D0%B2%D0%BE%D0%B1%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5',
            'color': 'text-amber-600',
            'name': 'Идёт частичное освобождение',
            'svg': 'halfInProgress'
        }
        fullInProgress = {
            'value': len(data[0]['fullInProgress']['noRisk']),
            'link': '/table_page?otsel_type=%D0%98%D0%B4%D1%91%D1%82+%D0%BF%D0%BE%D0%BB%D0%BD%D0%BE%D0%B5+%D0%BE%D1%81%D0%B2%D0%BE%D0%B1%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5&deviation=%D0%A0%D0%B0%D0%B1%D0%BE%D1%82%D0%B0+%D0%B7%D0%B0%D0%B2%D0%B5%D1%80%D1%88%D0%B5%D0%BD%D0%B0&deviation=%D0%91%D0%B5%D0%B7+%D0%BE%D1%82%D0%BA%D0%BB%D0%BE%D0%BD%D0%B5%D0%BD%D0%B8%D0%B9&deviation=%D0%A2%D1%80%D0%B5%D0%B1%D1%83%D0%B5%D1%82+%D0%B2%D0%BD%D0%B8%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F',
            'color': 'text-cyan-600',
            'name': 'Идёт полное освобождение',
            'svg': 'fullInProgress'
        }
        risk = {
            'value': len(data[0]["fullInProgress"]["risk"]),
            'link': '/table_page?otsel_type=%D0%98%D0%B4%D1%91%D1%82+%D0%BF%D0%BE%D0%BB%D0%BD%D0%BE%D0%B5+%D0%BE%D1%81%D0%B2%D0%BE%D0%B1%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5&deviation=%D0%9D%D0%B0%D1%81%D1%82%D1%83%D0%BF%D0%B8%D0%BB%D0%B8+%D1%80%D0%B8%D1%81%D0%BA%D0%B8',
            'color': 'text-rose-600',
            'name': 'Полное освобождение риски',
            'svg': 'risk'
        }
        notStarted = {
            'value': len(data[0]["notStarted"]),
            'link': '/table_page?otsel_type=%D0%9E%D1%81%D0%B2%D0%BE%D0%B1%D0%BE%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5+%D0%BD%D0%B5+%D0%BD%D0%B0%D1%87%D0%B0%D1%82%D0%BE',
            'color': 'text-neutral-500',
            'name': 'Освобождение не начато',
            'svg': 'notStarted'
        }

        result = [[done, halfInProgress, fullInProgress, risk, notStarted], chart_data]
        return result
    
    def get_building_details(self,building_id : int):
        return self.db.get_building_details(building_id)