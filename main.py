from modules.tools import (
                           GetPostUrls,
                           GetGroupNamesByLikers
                          )

from modules.data_parsers import (
    ParseTempData
)

import threading

if __name__ ==  '__main__':

    # result = GetGroupNamesByLikers(
    #     GetPostUrls().get()
    # ).run()
    
    ParseTempData().parse_data("final.csv")