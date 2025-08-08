 WITH unnest_actions_groups AS (
         SELECT "group".group_id,
            "group"."group",
            service_table.service_table,
            service.service,
            unnest("group".actions) AS action_id
           FROM auth."group"
             JOIN auth.service_table USING (service_table_id)
             JOIN auth.service USING (service_id)
        )
 SELECT unnest_actions_groups.group_id,
    unnest_actions_groups."group",
    unnest_actions_groups.service_table,
    unnest_actions_groups.service,
    array_agg(action.action) AS array_agg
   FROM unnest_actions_groups
     LEFT JOIN auth.action USING (action_id)
  GROUP BY unnest_actions_groups.group_id, unnest_actions_groups."group", unnest_actions_groups.service_table, unnest_actions_groups.service;