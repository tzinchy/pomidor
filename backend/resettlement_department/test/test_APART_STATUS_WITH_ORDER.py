import pytest
from insert import insert_test_data, truncate
from data.mock import order_decisions_test_data
from config import get_connection
import json

STATUS_MAPPING = {
    1: "Согласие",
    2: "Отказ",
    3: "Суд",
    4: "МФР Компенсация",
    5: "МФР Докупка",
    6: "Ожидание",
    7: "Ждёт одобрения",
    8: "Не подобрано",
    9: "МФР (вне района)",
    10: "МФР Компенсация (вне района)",
    11: "Свободная",
    16: "Подготовить смотровой",
    17: "Отказ (Выход из Суда)"
}


test_cases = [
    # Согласие (1) order
    (order_decisions_test_data[1], 7, 7),   # согласие -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[1], 2, 1),   # согласие -> отказ = согласие
    (order_decisions_test_data[1], 1, 1),   # согласие -> согласие = согласие
    (order_decisions_test_data[1], 6, 6),   # согласие -> ожидание = ожидание
    (order_decisions_test_data[1], 3, 3),   # согласие -> суд = согласие
    (order_decisions_test_data[1], 16, 16), # согласие -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[1], 4, 4),   # согласие -> МФР компенсация = МФР компенсация
    (order_decisions_test_data[1], 10, 10), # согласие -> МФР компенсация (вне района) = МФР компенсация (вне района)
    (order_decisions_test_data[1], 5, 5),   # согласие -> МФР докупка = МФР докупка
    (order_decisions_test_data[1], 9, 9),   # согласие -> МФР (вне района) = МФР (вне района)
    
    # Суд (3) order
    (order_decisions_test_data[3], 7, 7),   # суд -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[3], 2, 3),   # суд -> отказ = суд
    (order_decisions_test_data[3], 1, 1),   # суд -> согласие = суд
    (order_decisions_test_data[3], 6, 6),   # суд -> ожидание = ожидание
    (order_decisions_test_data[3], 3, 3),   # суд -> суд = суд
    (order_decisions_test_data[3], 16, 16), # суд -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[3], 4, 3),   # суд -> МФР компенсация = суд
    (order_decisions_test_data[3], 10, 3),  # суд -> МФР компенсация (вне района) = суд
    (order_decisions_test_data[3], 5, 3),   # суд -> МФР докупка = суд
    (order_decisions_test_data[3], 9, 3),   # суд -> МФР (вне района) = суд
    
    # order
    (order_decisions_test_data[4], 7, 7),   # МФР компенсация -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[4], 2, 4),   # МФР компенсация -> отказ = МФР компенсация
    (order_decisions_test_data[4], 1, 4),   # МФР компенсация -> согласие = МФР компенсация
    (order_decisions_test_data[4], 6, 6),   # МФР компенсация -> ожидание = ожидание
    (order_decisions_test_data[4], 3, 3),   # МФР компенсация -> суд = суд
    (order_decisions_test_data[4], 16, 16), # МФР компенсация -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[4], 4, 4),   # МФР компенсация -> МФР компенсация = МФР компенсация
    (order_decisions_test_data[4], 5, 4),   # МФР компенсация -> МФР докупка = МФР компенсация
    
    # order
    (order_decisions_test_data[10], 7, 7),  # МФР компенсация (вне района) -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[10], 2, 10), # МФР компенсация (вне района) -> отказ = МФР компенсация (вне района)
    (order_decisions_test_data[10], 1, 10), # МФР компенсация (вне района) -> согласие = МФР компенсация (вне района)
    (order_decisions_test_data[10], 6, 6),  # МФР компенсация (вне района) -> ожидание = ожидание
    (order_decisions_test_data[10], 3, 3),  # МФР компенсация (вне района) -> суд = суд
    (order_decisions_test_data[10], 16, 16),# МФР компенсация (вне района) -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[10], 5, 10), # МФР компенсация (вне района) -> МФР докупка = МФР компенсация (вне района)
    
    # order
    (order_decisions_test_data[9], 7, 7),   # МФР (вне района) -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[9], 2, 9),   # МФР (вне района) -> отказ = МФР (вне района)
    (order_decisions_test_data[9], 1, 9),   # МФР (вне района) -> согласие = МФР (вне района)
    (order_decisions_test_data[9], 6, 6),   # МФР (вне района) -> ожидание = ожидание
    (order_decisions_test_data[9], 3, 3),   # МФР (вне района) -> суд = суд
    (order_decisions_test_data[9], 16, 16), # МФР (вне района) -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[9], 5, 9),   # МФР (вне района) -> МФР докупка = МФР (вне района)
    
    # order
    (order_decisions_test_data[5], 7, 7),   # МФР докупка -> ждёт одобрения = ждёт одобрения
    (order_decisions_test_data[5], 2, 5),   # МФР докупка -> отказ = МФР докупка
    (order_decisions_test_data[5], 1, 5),   # МФР докупка -> согласие = МФР докупка
    (order_decisions_test_data[5], 6, 6),   # МФР докупка -> ожидание = ожидание
    (order_decisions_test_data[5], 3, 3),   # МФР докупка -> суд = суд
    (order_decisions_test_data[5], 16, 16), # МФР докупка -> подготовить смотровой = подготовить смотровой
    (order_decisions_test_data[5], 5, 5),   # МФР докупка -> МФР докупка = МФР (вне района)
]

@pytest.mark.parametrize('order_data,change_status,expected_status', test_cases)
def test_order_decisions(order_data, change_status, expected_status):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 1. Upsert order data
            cols = order_data.keys()
            vals = list(order_data.values())
            set_expr = ', '.join([f"{k} = EXCLUDED.{k}" for k in cols])
            
            cursor.execute(
                f"""
                INSERT INTO order_decisions ({','.join(cols)})
                VALUES ({','.join(['%s']*len(vals))})
                ON CONFLICT (order_id) DO UPDATE
                SET {set_expr}
                """,
                vals
            )
            connection.commit()
            # 2. Update offer status
            cursor.execute(
                """UPDATE offer SET
                new_aparts = jsonb_set(
                    COALESCE(new_aparts, '{}'::jsonb),
                    '{2001}', 
                    jsonb_build_object('status_id', %s)
                )
                WHERE offer_id = 6""",
                (change_status,)
            )
            connection.commit()
            # 3. Verify old_apart status
            cursor.execute(
                "SELECT status_id FROM old_apart WHERE affair_id = 1002"
            )
            result = cursor.fetchone()
            actual_status = result[0] if result else None
            
            assert actual_status == expected_status, (
                f"{order_data['status_id']} -> "
                f"{change_status} expected "
                f"{expected_status}, got "
                f"{actual_status}"
            )
            
    finally:
        connection.close()
        