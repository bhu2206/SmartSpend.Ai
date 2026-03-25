import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_expense():
    try:
        df = pd.read_csv("data.csv")
    except:
        return None

    if len(df) < 5:
        return None

    df["Day"] = range(len(df))

    X = df[["Day"]]
    y = df["Amount"]

    model = LinearRegression()
    model.fit(X, y)

    future_day = [[len(df) + 7]]
    prediction = model.predict(future_day)

    return prediction[0]