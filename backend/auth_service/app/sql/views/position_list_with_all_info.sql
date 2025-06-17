 SELECT p.position_id,
    jsonb_build_object('position', pl."position", 'management', m.management, 'division', d.division, 'reports_to',
        CASE
            WHEN p.obey_id IS NOT NULL THEN jsonb_build_object('position_id', p.obey_id, 'position', obey_pl."position", 'management', obey_m.management, 'division', obey_d.division)
            ELSE NULL::jsonb
        END) AS position_info
   FROM auth."position" p
     LEFT JOIN auth.position_list pl USING (position_list_id)
     LEFT JOIN auth.management m USING (management_id)
     LEFT JOIN auth.division d USING (division_id)
     LEFT JOIN auth.department dp USING (department_id)
     LEFT JOIN auth."position" obey ON p.obey_id = obey.position_id
     LEFT JOIN auth.position_list obey_pl ON obey.position_list_id = obey_pl.position_list_id
     LEFT JOIN auth.management obey_m ON obey.management_id = obey_m.management_id
     LEFT JOIN auth.division obey_d ON obey.division_id = obey_d.division_id;