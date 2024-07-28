import pandas as pd
import glob


files = glob.glob("../data/*.csv")
df_list = []
for file in files:
    df = pd.read_csv(file, index_col=False)
    df_list.append(df)

combined_df = pd.concat(df_list, axis=0, ignore_index=False)
combined_df.sort_values(by="Auction Date", inplace=True)
combined_df.dropna(subset="Price per $100", inplace=True)
print(combined_df[combined_df['Auction Date'] == "01/04/2023"])
#combined_df.to_csv("combined_data.csv", index=False)