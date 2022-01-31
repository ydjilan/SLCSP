# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 14:27:41 2022
With Spyder 4.1.5 and Python 3.8.5

@author: TBD

Coding Assignment - SLCSP https://homework.adhoc.team/slcsp/

Make sure you save your 3 files on your appropriate directory 

"""




import pandas as pd 
import sys

plandf = pd.read_csv('U:\My Documents\Personal\Training\Py\slcsp\plans.csv',  engine='python')

plandf.info()


###### subset to Silver plan
silverplandf = plandf[plandf["metal_level"] == "Silver"]


### I wasn't sure if a real tuple type is needed since it was mentioned; but I just went with a combination of fields to create a unique key
# plandf["SRateArea"] = plandf["state"] + " " +  plandf["rate_area"].astype (str)

silverplandf["SRateArea"] = silverplandf["state"] + " " +  silverplandf["rate_area"].astype (str)

silverplandf["SRateArea"].describe()


#### Creating multiple "temporary" tables for manipulation and validation 

aaa= silverplandf.sort_values(by=["SRateArea", "rate"])


### aaa is the main dataset that will be used to slice things out

aaa["Id"] = aaa["SRateArea"] + "-" + aaa["rate"].astype(str)



### to identify Silver plan with less than 2 rates
bbbb= silverplandf.groupby(["SRateArea", "metal_level"]).size()






##############

# Grabbing the lowest plan(s) for each state and rate area - flag them for deletion in the main dataset (aaa)

bbb = aaa.groupby("SRateArea")["rate"].nsmallest(n=1, keep = "all")

bbb1 = pd.DataFrame(bbb).reset_index()

bbb1["Delete"] = 1
bbb2 = bbb1.drop(["level_1"], axis =1)

bbb2["Id"] = bbb2["SRateArea"] + "-" + bbb2["rate"].astype(str)

bbb2.info()


ccc = pd.merge(aaa, bbb2, how="left", on ="Id", indicator= True)
ccc.info()

ccc1 = ccc[ccc["Delete"] != 1]
ccc1["_merge"].describe()



##### probably not needed anymore 
ccc2 = ccc1.drop(["_merge"], axis =1)



##### after deletign all the lowest rate above, I am tackling the 2nd lowest ones

ddd = ccc1.groupby("SRateArea_x")["rate_x"].nsmallest(n=1, keep = "first")

ddd1 = pd.DataFrame(ddd).reset_index()
ddd1["SRateArea_x"].describe()  #### and just checking that there are no areas with more than 1 rate



##### flagging this cohort to keep 
ddd1["keep"] = 1
ddd2 = ddd1.drop(["level_1"], axis =1)

ddd2["Id"] = ddd2["SRateArea_x"] + "-" + ddd2["rate_x"].astype(str)

ddd2.info()


##### eee will be run through the rest of the codes; but I cretaed fff as a validation check

eee = pd.merge(aaa, ddd2, how="left", on ="Id", indicator= True)
fff = pd.merge(ccc2, ddd2, how="left", on ="Id", indicator= True)

eee1 = eee[eee["keep"] == 1]
fff1 = fff[fff["keep"] == 1]

eee1.info()
fff1.info()




###
# ZIPS FILE
###

zips = pd.read_csv('U:\My Documents\Personal\Training\Py\slcsp\zips.csv',  engine='python')

zips.info()
zips["zipcode"].mode()

zips["SRateArea"] = zips["state"] + " " +  zips["rate_area"].astype (str)


##### Merging the 2nd lowest plans computed above with the Zipcode file

eee2 = eee1.drop(["_merge"], axis =1)

zplan = pd.merge(eee2, zips, how = "outer", on ="SRateArea", indicator= True )

zplan1 = zplan.drop(["_merge"], axis =1)



###
# BRINGING SLCSP FILE for final output
###

slcsp = pd.read_csv('U:\My Documents\Personal\Training\Py\slcsp\slcsp.csv',  engine='python')
slcsp.info()

alll = pd.merge(slcsp, zplan1, how = "outer", on = "zipcode", indicator = True)
alll.info()


all1 = alll[alll["_merge"] == "both"]

### testing the above - the both datasets have 100 records  allllllll = pd.merge(slcsp, zplan1, how = "left", on = "zipcode", indicator = True)


alll1 = all1.drop(["_merge", "rate_area_y", "state_y","keep", "rate_x", "SRateArea_x", "Id", "metal_level", "county_code", "name", "plan_id"  ], axis = 1)
alll2 = alll1.drop_duplicates()

#### now, let's table the zip codes with multiple rate areas

alll2_1 = alll2.drop(["state_x", "rate_area_x" ], axis = 1)

alll3 = alll2_1.groupby("zipcode").agg({'zipcode': 'count'})
alll3.info()

alll3["count"] = alll3["zipcode"]
alll31 = alll3.drop(["zipcode"], axis = 1)


ab = pd.DataFrame(alll31).reset_index()
ab.info()


ab1 = ab[ab["count"] != 1]


alll4 = pd.merge(alll2_1, ab1, how = "outer", on = "zipcode", indicator = True )

alll4.info()


alll44 = alll4.drop ([ "SRateArea", "count"] , axis = 1)


####turning the zipcodes as a 5 characters zip for the final output
alll44["aaa"] = alll44["zipcode"].astype(str).str[:-2]

alll444 = alll44.drop ([  "zipcode"] , axis = 1)


#### Setting the zip with multiple rates into blank 
alll444.loc[alll444["_merge"] != "both", " rate"] = alll444["rate_y"]
####  Not really needed  alll444.loc[alll444["_merge"] == "both", " rate"] = ""


alll5 = alll444.drop (["rate_y",  "_merge"] , axis = 1)
alll6 = alll5.drop_duplicates()


alll7 = alll6.rename(columns={"aaa": "zipcode"})

alll7.info()


##### THERE ARE SOME NAN THAT I COULD CONVERT INTO BLANK, BUT THE STDOUT IS ALREADY TAKING CARE OF THAT AS REQUESTED
alll7.to_csv(sys.stdout, index=False , float_format = "%.2f")



#################  TESTING Script 

### 1- We can visually test the recommended formats in the stdout

alll7.to_csv(sys.stdout, index=False , float_format = "%.2f")

### 2- Testing 2 -  the order of the rows in your answer as emitted on stdout must stay the same as how they appeared in the original slcsp.csv. 

import numpy as np

slcsp1 = slcsp
slcsp1["new_id"] = np.arange(slcsp1.shape[0])

slcsp1.info()

alll8 = alll7
alll8["new_id"] = np.arange(alll8.shape[0])

alll8.info()



test = pd.merge(slcsp1, alll8, how = "outer", on = "new_id", indicator = True )

test.info()

test["zip"] = test["zipcode_y"].astype(int)
test["Diff"] = test["zip"] - test["zipcode_x"]

##### Might not be the most efficient ways, but the rows in this Diff column should equal to 0 when the order of the zipcodes in the SLCSP file is the same as the final file with the rates. 
