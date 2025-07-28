 SELECT department.department_id,
    department.department,
    management.management_id,
    management.management,
    division.division_id,
    division.division
   FROM auth.management
     JOIN auth.division USING (management_id)
     JOIN auth.department USING (department_id)
  ORDER BY department.department_id, management.management_id, division.division_id;