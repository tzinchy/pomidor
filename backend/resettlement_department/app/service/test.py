import psycopg2
from core.config import settings
from repository.database import project_managment_session
from sqlalchemy import text

def get_db_connection():
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME,
    )


async def rematch(apart_ids):
    cant_offer_aparts_raise_ids = {}
    async with project_managment_session() as session:
        for apart_id in apart_ids:
            apart_query = text("""
                with unnst_max_rank AS (
                    select affair_id, (key)::bigint as new_apart_id, value->>'status_id' as status_id 
                    from public.offer, jsonb_each(new_aparts)
                    where (value->>'status_id')::integer != 1  
                ),
                unnst_join AS (
                    SELECT 
                        affair_id,
                        new_apart_id,
                        room_count, 
                        max(rank) as max_rank
                    FROM unnst_max_rank
                    join new_apart using (new_apart_id)
                    group by affair_id, new_apart_id, room_count, status_id
                ),
                build_max_rank_json AS (
                    SELECT affair_id, jsonb_object_agg(room_count::integer, max_rank) as max_rank_by_room_count 
                    from unnst_join
                    where affair_id = :apart_id
                    group by affair_id
                )
                SELECT 
                    build_max_rank_json.affair_id,
                    room_count, 
                    full_living_area,
                    total_living_area,
                    living_area, 
                    is_special_needs_marker, 
                    is_queue,
                    queue_square,
                    new_house_addresses, 
                    rank, 
                    max_rank_by_room_count
                FROM build_max_rank_json 
                JOIN old_apart USING (affair_id)
                JOIN history USING (history_id)
                """)
            
            apart_info_result = await session.execute(apart_query, {"apart_id": apart_id})
            apart_info = apart_info_result.fetchone()._mapping if apart_info_result.rowcount > 0 else None

            if not apart_info:
                continue

            # Check approved apartments
            check_approved_query = text("""
                SELECT jsonb_object_agg(key::text, value) as approved_aparts
                FROM (
                    SELECT key, value 
                    FROM offer, jsonb_each(new_aparts)
                    WHERE affair_id = :apart_id
                    AND (value->>'status_id')::int = 1
                ) approved_aparts;
            """)

            approved_result = await session.execute(check_approved_query, {"apart_id": apart_id})
            approved_aparts = approved_result.scalar() or {}

            # Check declined apartments
            check_declined_query = text("""
                WITH declined_aparts AS (
                    SELECT (key)::int as new_apart_id, (value->>'decline_reason_id')::int as decline_reason_id
                    FROM offer, jsonb_each(new_aparts)
                    WHERE (value->>'status_id')::int = 2 AND offer_id = (SELECT max(offer_id) FROM offer WHERE affair_id = :apart_id)
                )
                SELECT 
                    new_apart_id, 
                    json_build_object(
                        'room_count', new_apart.room_count,
                        'min_floor', decline_reason.min_floor,
                        'max_floor', decline_reason.max_floor
                    ) AS decline_info
                FROM declined_aparts
                JOIN decline_reason USING (decline_reason_id)
                JOIN new_apart USING (new_apart_id);
            """)
            
            declined_result = await session.execute(check_declined_query, {"apart_id": apart_id})
            declined_aparts = [row._mapping for row in declined_result]

            max_ranks = apart_info.get('max_rank_by_room_count', {})
            for declined in declined_aparts:
                room_count = str(declined['decline_info']['room_count'])
                if room_count in max_ranks:
                    declined['decline_info']['max_rank'] = max_ranks[room_count]
            
            print(apart_info)
            print('\n')
            print(declined_aparts)
            print('\n')
            print(approved_aparts)
            for declined in declined_aparts:
                decline_reason = declined['decline_info']
                decline_reason = {
                    'rank' : apart_info.get('rank'),
                    'full_living_area' : apart_info.get('full_living_area'),
                    'total_living_area' : apart_info.get('total_living_area'),
                    'living_area' : apart_info.get('living_area'),
                    'new_house_addresses' : apart_info.get('new_house_addresses')
                }
                print(decline_reason)
                new_apart_query = '''SELECT new_apart_id, room_count, full_living_area, total_living_area, living_area, rank 
                        FROM public.new_apart
                        WHERE new_apart_id::text NOT IN 
                            (SELECT key FROM public.offer, 
                            LATERAL json_each_text(new_aparts::json) AS j(key, value) 
                            WHERE (value::json->>'status_id')::int != 2)
                        AND room_count = :room_count
                        AND full_living_area >= :full_living_area 
                        AND total_living_area >= :total_living_area
                        AND living_area >= :living_area
                        AND for_special_needs_marker = :is_special_needs_marker
                        AND house_address IN {}
                        AND rank IN (:rank, :max_rank_by_room_count)
                        AND new_apart_id::text NOT IN 
                            (SELECT key FROM public.offer, LATERAL json_each_text(new_aparts::json) AS j(key, value) 
                            WHERE affair_id = :apart_id)
                        ORDER BY rank, (full_living_area + living_area) 
                        LIMIT 1'''
                

    return cant_offer_aparts_raise_ids


