 WITH unnest_district AS (
         SELECT DISTINCT district_group.district_group_id,
            unnest(district_group.districts_ids) AS district_id
           FROM auth.district_group
        ), join_district AS (
         SELECT unnest_district.district_group_id,
            district.district
           FROM unnest_district
             JOIN auth.district USING (district_id)
        )
 SELECT district_group_id,
    array_agg(district) AS districts
   FROM join_district
  GROUP BY district_group_id;