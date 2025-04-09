from service.apartment_insert import insert_data_to_new_apart
import pandas as pd


if __name__ == "__main__":

    df = pd.read_excel('/Users/viktor/Desktop/programs/RSM/export_new_aparts.xlsx')
    result = insert_data_to_new_apart(df)
    print(result)