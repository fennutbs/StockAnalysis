import csv

df_mv = []


def data_reload(str, df_mv):
    with open('./data/' + str, 'r', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            df_mv.append(row)
        return df_mv
