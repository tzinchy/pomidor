 WITH unnest_actions_groups AS (
         SELECT "group".group_id,
            unnest("group".actions) AS action_id
           FROM auth."group"
             JOIN auth.service_table USING (service_table_id)
             JOIN auth.service USING (service_id)
        )
 SELECT unnest_actions_groups.group_id,
    array_agg(action.action) AS array_agg
   FROM unnest_actions_groups
     LEFT JOIN auth.action USING (action_id)
  GROUP BY unnest_actions_groups.group_id;