import datetime
from datetime import date
from threading import Thread
from typing import Dict

import pandas as pd
from filecache import filecache

weather_data = {
    i: pd.read_excel(f"/app/processing/weather_data/{i}.xls", skiprows=6)
    for i in range(1, 53)
}

# функция для расчета вероятности заболевания если удовлетворены начальные условия заболевания
def get_prob(t_and_hum_df, optim_t, optim_u, special_condition=False):
    mean_T = t_and_hum_df["T"].mean()
    mean_U = t_and_hum_df["U"].mean()

    prob_T = 1 - (abs(optim_t - mean_T) / optim_t)
    prob_U = 1 - (abs(optim_u - mean_U) / optim_u)

    if not special_condition:
        return round(100 * (prob_T + prob_U) / 2, 2)
    return round(100 * (prob_T + prob_U + 1) / 3, 2)


# функция, чтобы определить, какие осадки будут в течение дня
def check_rain(day_entries):
    if "град" in "".join(day_entries.tolist()).lower():
        return "ожидается град"
    elif "ливень" in "".join(day_entries.tolist()).lower():
        return "ожидается ливень"
    elif "дождь" in "".join(day_entries.tolist()).lower():
        return "ожидается дождь"
    elif "снег" in "".join(day_entries.tolist()).lower():
        return "ожидается снег"
    else:
        return "не ожидается осадков"


# главная функция - подсчет вероятностей
# на вход подается дата и датасет
# на выходе словарь с вероятностями и прогноз погоды на следующие три дня
@filecache
def forecast(current_date: date, key: int) -> Dict:
    df: pd.DataFrame = weather_data[key]
    df["date"] = pd.to_datetime(df[df.columns[0]], dayfirst=True)
    df["WW"] = df["WW"].fillna("")

    pd_cur_date = pd.to_datetime(current_date)

    df_slice = df[
        (df["date"] >= pd_cur_date)
        & (df["date"] < pd_cur_date + datetime.timedelta(days=4))
    ]

    t_and_hum_by_day = df_slice.groupby([pd.Grouper(key="date", freq="D")])[
        ["T", "U"]
    ].mean()
    t_and_hum_by_day["T"] = t_and_hum_by_day["T"].round(2)
    t_and_hum_by_day["U"] = t_and_hum_by_day["U"].round(2)

    if (
        len(
            df_slice[
                df_slice["WW"].str.contains(
                    "ливень|дождь|снег|град|гроза|морось|мгла|туман|морось",
                    case=False,
                    na=False,
                )
            ]
        )
        == 0
    ):
        any_precipitation = False
    else:
        any_precipitation = True

    if len(df_slice[df_slice["WW"].str.contains("ливень", case=False, na=False)]) > 70:
        showers = True
    else:
        showers = False

    day_forecast_precipitation = (
        df_slice.groupby(pd.Grouper(key="date", freq="D"))["WW"]
        .apply(lambda x: check_rain(x))
        .reset_index()
    )
    weather_forecast_df = (
        t_and_hum_by_day.iloc[1:]
        .reset_index()
        .merge(day_forecast_precipitation, on=["date"], how="left")
    )
    weather_forecast_df = weather_forecast_df.set_index("date")
    weather_forecast_df.index = weather_forecast_df.index.strftime("%Y-%m-%d")

    # 1) Милдью или ложная мучнистая роса
    if all(t_and_hum_by_day["U"].values >= 85) and all(
        t_and_hum_by_day["T"].values >= 11
    ):
        mildew_prob = get_prob(t_and_hum_by_day, 23, 100)
    else:
        mildew_prob = 0

    # 2) Оидиум – конидии
    if all(t_and_hum_by_day["T"].values >= 5) and all(
        t_and_hum_by_day["U"].values >= 55
    ):
        conidia_prob = get_prob(t_and_hum_by_day, 20, 70)
    else:
        conidia_prob = 0

    # 3) Оидиум - мицелий
    if all(t_and_hum_by_day["T"].values >= 5) and all(
        t_and_hum_by_day["U"].values >= 55
    ):
        if any_precipitation is False:
            mycelium_prob = get_prob(t_and_hum_by_day, 30, 70, special_condition=True)
        else:
            mycelium_prob = get_prob(t_and_hum_by_day, 30, 70)
    else:
        mycelium_prob = 0

    # 4) Антракноз
    if all(t_and_hum_by_day["T"].values >= 10) and all(
        t_and_hum_by_day["U"].values >= 60
    ):
        anthracnose_prob = get_prob(t_and_hum_by_day, 27, 75)
    else:
        anthracnose_prob = 0

    # 5) Серая гниль
    if all(t_and_hum_by_day["T"].values >= 12) and all(
        t_and_hum_by_day["U"].values > 90
    ):
        gray_rot_prob = get_prob(t_and_hum_by_day, 27.5, 100)
    else:
        gray_rot_prob = 0

    # 6) Чёрная пятнистость
    if all(t_and_hum_by_day["T"].values >= 15) and all(
        t_and_hum_by_day["U"].values > 75
    ):
        black_spot_prob = get_prob(t_and_hum_by_day, 19, 87.5)
    else:
        black_spot_prob = 0

    # 7) Черная гниль
    if all(t_and_hum_by_day["T"].values >= 15) and all(
        t_and_hum_by_day["U"].values > 90
    ):
        black_rot_prob = get_prob(t_and_hum_by_day, 22.5, 100)
    else:
        black_rot_prob = 0

    # 8) Белая гниль
    if all(t_and_hum_by_day["T"].values >= 14) and all(
        t_and_hum_by_day["U"].values > 80
    ):
        if showers:
            white_rot_prob = get_prob(
                t_and_hum_by_day, 23.5, 100, special_condition=True
            )
        else:
            white_rot_prob = get_prob(t_and_hum_by_day, 23.5, 100)
    else:
        white_rot_prob = 0

    # 9) Вертициллезное увядание (вилт)
    if all(t_and_hum_by_day["T"].values >= 18) and all(
        t_and_hum_by_day["U"].values > 80
    ):
        wilt_prob = get_prob(t_and_hum_by_day, 22.5, 100)
    else:
        wilt_prob = 0

    # 10) Альтернариоз
    if all(t_and_hum_by_day["T"].values >= 11) and all(
        t_and_hum_by_day["U"].values > 72.5
    ):
        alternariosis_prob = get_prob(t_and_hum_by_day, 24, 87.5)
    else:
        alternariosis_prob = 0

    # 11) Фузариоз
    if all(t_and_hum_by_day["T"].values >= 1) and all(
        t_and_hum_by_day["U"].values > 40
    ):
        fusarium_prob = get_prob(t_and_hum_by_day, 16.5, 85)
    else:
        fusarium_prob = 0

    # 12) Краснуха
    if all(t_and_hum_by_day["T"].values >= 11) and all(
        t_and_hum_by_day["U"].values > 80
    ):
        rubella_prob = get_prob(t_and_hum_by_day, 19, 95)
    else:
        rubella_prob = 0

    # 13) Бактериальный рак
    if all(t_and_hum_by_day["T"].values >= 17) and all(
        t_and_hum_by_day["U"].values > 80
    ):
        bacterial_cancer_prob = get_prob(t_and_hum_by_day, 27.5, 95)
    else:
        bacterial_cancer_prob = 0

    return {
        "date": pd_cur_date.strftime("%Y-%m-%d"),
        "illnesses": {
            "Милдью": mildew_prob,
            "Оидиум – конидии": conidia_prob,
            "Оидиум - мицелий": mycelium_prob,
            "Антракноз": anthracnose_prob,
            "Серая гниль": gray_rot_prob,
            "Чёрная пятнистость": black_spot_prob,
            "Черная гниль": black_rot_prob,
            "Белая гниль": white_rot_prob,
            "Вертициллезное увядание": wilt_prob,
            "Альтернариоз": alternariosis_prob,
            "Фузариоз": fusarium_prob,
            "Краснуха": rubella_prob,
            "Бактериальный рак": bacterial_cancer_prob,
        },
    } | {"weather_forecast": weather_forecast_df.T.to_dict()}
