import numpy as np
import pandas as pd
from service.apartment_insert import insert_data_to_new_apart, insert_data_to_old_apart
from service.order_insert import insert_data_to_order_decisions

df = pd.read_excel("/Users/arsenijkarpov/pomidor/backend/resettlement_department/app/kpu.xlsx")
insert_data_to_new_apart(df)

# df = pd.DataFrame({
#     "area_id": ["1", "2", "3", np.nan],
#     "order_id": [1, 1, 3, 4],
#     "new": ["doi", "oijhg", "ihg", "jhg"]
# })
# def concat_area_id_agg(series: pd.Series):
#     if series.name != "area_id":
#         return series.iloc[0]
#     if len(series) > 1:
#         out = {}
#         for i, v in enumerate(series):
#             out[str(i)] = v
#         return out
#     else:
#         return series.apply(lambda x: {"0": x})
# df = df.groupby("order_id").agg(concat_area_id_agg).reset_index()
# def foo(x: dict):
#     for k, v in x.items():
#         if v is np.nan:
#             x[k] = "NULL"
#     return x

# print(df)
# df["area_id"] = df["area_id"].apply(foo)
# print(df)
