from os import listdir, remove
import pandas as pd
from itertools import chain 

class ParseTempData():

    TEMP_DIRECTORY = "temp"

    def __parse_output_name(self, name):
        return name.replace(".csv", "").replace(".","")

    def parse_data(self, output_name: str, do_temp_clean=True) -> bool:
        names = []
        for file in listdir(self.TEMP_DIRECTORY):
            path = f"{self.TEMP_DIRECTORY}/{file}"
            dataframe = pd.read_csv(path)
            names.append([name for name in dataframe['names']])
            if do_temp_clean:
                remove(path)
        final_dataframe = pd.DataFrame()
        final_dataframe['names'] = list(chain(*names)) 
        final_dataframe = final_dataframe['names'].value_counts()
        final_dataframe.to_csv(f"{self.__parse_output_name(output_name)}.csv")
        return True 