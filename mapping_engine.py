import pandas as pd
from paths import resource_path

def load_vendor_map():
    df = pd.read_csv(resource_path("vendor_map_AL_to_vendor.csv"))
    df = df.rename(columns={"AL_Name": "AL_Name_map"})
    return df
