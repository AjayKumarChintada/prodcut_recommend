from tokenize import group
from scipy.spatial.distance import cosine
import numpy as np
from numpy.linalg import norm

import re
import pandas as pd
def weight_processor(weight_string):
    """
    takes - weight_string
        ex: 1 kg 200 g, 
    returns - weight in kg with no units
        ex: 1.2000
    """
    # can handle, 1 kg 200 g, 1.2 kg 
    pattern1 = r".*(\b\d+).*(\b\d+).*"
    # can handle 1 kg, 2 kg
    pattern2 = r".*(\b\d+).*"

    result_pat1 = re.search(pattern1, weight_string)

    if result_pat1:
        groups = result_pat1.groups()
        kg = float(groups[0])
        gm = float(groups[1])
        return kg + gm / 1000
        # return float(groups[0] + "." + groups[1])
    
    result_pat2 = re.search(pattern2, weight_string)

    if result_pat2:
        groups = result_pat2.groups()
        weight = float(groups[0])
        if weight > 100:
            return weight / 1000
        return float(weight)



def storage_processor(storage_string):
    """
    takes - storage_string
        ex: 1 TB, 4 GB
    return -
        1 TB -> 1024, 4 Gb -> 4
    """
    # 1 Tera byte
    # 1 giga byte
    tb_pattern = r".*(\b\d+)(\s+)[tT].*"
    gb_pattern = r".*(\b\d+)(\s+)[gG].*"

    result_tbpat = re.search(tb_pattern, storage_string)
    if result_tbpat:
        print("tb matched")
        groups = result_tbpat.groups()
        return float(groups[0]) * 1024
    
    result_gbpat = re.search(gb_pattern, storage_string)
    if result_gbpat:
        print("gb matched")
        groups = result_gbpat.groups()
        return float(groups[0])


# cpu power
def processor_speed(speed_string):

    #take 2.4 GHz and show as 2.4
    ghz_pattern_Decimal = r".*(\b\d+).*(\b\d+)(\s)[GHz].*"
    ghz_pattern_NoDecimal = r".*(\b\d+)(\s)[GHz].*"


    result_ghz_decimal = re.search(ghz_pattern_Decimal, speed_string)
    if result_ghz_decimal:    
        print("ghz value is")
        groups = result_ghz_decimal.groups()
        value = float(groups[0]) + float(groups[1])/10
        return (value)
    
    result_ghz_Nodecimal = re.search(ghz_pattern_NoDecimal, speed_string)
    if result_ghz_Nodecimal:    
        print("ghz value is")
        groups = result_ghz_Nodecimal.groups()
        value = float(groups[0])
        return (value)


#battery life
def battery_life(batteryLife_string):
    #6 hours to 6
    battery_life_pattern_Decimal = r".*(\b\d+).*(\b\d+)(\s)[Hours].*"
    battery_life_pattern_NoDecimal = r".*(\b\d+)(\s)[Hours].*"

    result_battery_decimal = re.search(battery_life_pattern_Decimal, batteryLife_string)
    if result_battery_decimal:    
        print("battery life is")
        groups = result_battery_decimal.groups()
        value = float(groups[0]) + float(groups[1])/10
        return (value)
    
    result_battery_Nodecimal = re.search(battery_life_pattern_NoDecimal, batteryLife_string)
    if result_battery_Nodecimal:    
        print("battery life is")
        groups = result_battery_Nodecimal.groups()
        value = float(groups[0])
        return (value)




#screen size
def screen_size(screensize_string):
    #take 13.5 inches and convert to 13.5
    #take 30 centimeters and convert to 30/2.54 = 12
    inch_pattern_decimal = r".*(\b\d+).*(\b\d+)(\s)[Inches].*"
    inch_pattern_nodecimal = r".*(\b\d+)(\s)[Inches].*"
    cm_pattern_decimal = r".*(\b\d+).*(\b\d+)(\s)[Centi].*"
    cm_pattern_nodecimal = r".*(\b\d+)(\s)[Centi].*"

    result_screen_In_decimal = re.search(inch_pattern_decimal, screensize_string)
    if result_screen_In_decimal:    
        print("screen size is")
        groups = result_screen_In_decimal.groups()
        value = float(groups[0]) + float(groups[1])/10
        return (value)
    
    result_screen_In_Nodecimal = re.search(inch_pattern_nodecimal, screensize_string)
    if result_screen_In_Nodecimal:    
        print("screen size is")
        groups = result_screen_In_Nodecimal.groups()
        value = float(groups[0])
        return (value)

    result_screen_cm_decimal = re.search(cm_pattern_decimal, screensize_string)
    if result_screen_cm_decimal:    
        print("screen size is")
        groups = result_screen_cm_decimal.groups()
        value = float(groups[0]) + float(groups[1])/10
        return (value/2.54)
    
    result_screen_cm_Nodecimal = re.search(cm_pattern_nodecimal, screensize_string)
    if result_screen_cm_Nodecimal:    
        print("screen size is")
        groups = result_screen_cm_Nodecimal.groups()
        value = float(groups[0])
        return (value/2.54)


    
if __name__ == "__main__":
    print(weight_processor("2 kg 200 grams"))

    # laptop_data = pd.read_csv("test.csv")
    # weights = laptop_data["Item Weight"]
    # laptop_data["Weight Num"] =  laptop_data["Item Weight"].apply(weight_processor)
    # min_weight = laptop_data["Weight Num"].min()
    # laptop_data["Weight Num"] =  laptop_data["Item Weight"].apply(weight_processor)
    # # min_weight = laptop_data["Weight Num"].min()
    # # max_weight = laptop_data["Weight Num"].max()
    # # laptop_data["Weight Num"] = laptop_data["Weight Num"].apply(lambda x : (x - min_weight) / (max_weight - min_weight)) * 100

    # question1 = "How often you travell along with your laptop?"
    # print(question1)
    # q1_options = {
    #     "0":{
    #         "text": "yes, I travell a lot.",
    #         "vector": [1.5]
    #     },
    #     "1":{
    #         "text": "Not much, Usaully stay at my desk.",
    #         "vector": [3]
    #     },
    #     "2":{
    #         "text": "Do not have any specification .",
    #         "vector": [2.25]
    #     },

    # }

    # inp = input()
    # user_vector = q1_options[inp]["vector"]
    # print("user vec", user_vector)
    # #laptop_data["cosine similarity"] = laptop_data["Weight Num"].apply(lambda x: 1 - cosine([x], user_vector))
    
    # cosine_sims = []
    # # [100], [100]
    # for i in laptop_data["Weight Num"]:
    #     A = np.array(user_vector)
    #     B = np.array([i])
    #     cosine = np.dot(A,B)/(norm(A)*norm(B))
    #     print("Cosine Similarity:", cosine)
        
        
        
    

# List1 = [4, 47, 8, 3]
# List2 = [3, 52, 12, 16]
# result = 1 - spatial.distance.cosine(List1, List2)print(result)
   


    




