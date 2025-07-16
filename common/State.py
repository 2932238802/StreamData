
import pandas as pd
from typing import Optional

class State:
    def __init__(self):
        # Optional[某个类型] 是一个类型提示
        self.dataframe: Optional[pd.DataFrame] = None
        self.result_df: Optional[pd.DataFrame] = None
        self.file_name:str = ""
        self.file_name_out:str = ""

