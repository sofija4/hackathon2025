import pandas as pd

df = pd.read_csv("toys.csv")  # or your actual CSV filename

df["url"] = df["name"].apply(lambda x: f"https://www.google.com/search?q={x.strip().replace(' ', '+')}+toy")

df.to_csv("toys.csv", index=False)  # overwrite the original file