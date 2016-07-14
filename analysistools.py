import pandas as pd
import numpy as np
import json
import os

def get_info(state, linecode):
    """Gets full state information for a given line code. 
    Returns: DataFrame    
    """
    # Only selects data where GeoName = State and LineCode = linecode and strips irrelevant information
    return data.ix[(data['GeoName'] == state) & (data['LineCode'] == linecode)].T[4:]

def get_state(state,year,excludes=None,reference=None):
    year = str(year) # Ensure string value
    if not reference: # If none, then mod = 1
        mod = 1
    else: # Any other case
        mod = int((data.ix[(data['GeoName'] == state) & (data['LineCode'] == str(reference))][year]).iloc[0]) # Population at reference line code
    if excludes: # If not none
        excludes = [str(x) for x in excludes] # Ensure string values
        return np.array([int(x) for x in data.ix[(data['GeoName'] == state) & (~data['LineCode'].isin(excludes))][year]])/mod # Returns all cases where GeoName = State and LineCode is not in excludes
    return np.array([int(x) for x in data.ix[(data['GeoName'] == state)]])/mod # Same as above, but with no excludes

def load_json(filename):
    with open(filename,'r') as f:
        json_data = json.load(f)
    return json_data
    
def sort_dict(cor):
    return sorted(cor.items(), key = lambda x:x[1])

def compare_to_state(s,states):
    print("\nRunning: {}".format(s))
    s_filename = s.lower().replace(" ","_")
    # Filters out LineCodes used in the function get_state (Line 12)
    exc = [1,10,20,40,50,60,80,90,510,530,2000,2001,2002,2010,2011,2012]
    # Iterate through all years 
    for year in range(2004,2015): # This does 2004 to 2014
    # Empty dictionary to hold correlation coefficient
        cor = {}
        print("   Computing correlation coefficients for {} in the year {}".format(s,year),end='\r')
    # Iterate through states
        for z in states:
            if z == s: # Skips the step in loop if the state is 's'
                continue
            state = get_state(z,year,excludes=exc,reference=1) # Gets information for arbitrary state 'z'
            s_info = get_state(s,year,excludes=exc,reference=1) # 's'-specific information
            val = np.corrcoef(state,s_info) # Calculate correlation coefficient
            cor[z] = val[0,1] # Takes value from top right index from array and puts it in the dictionary with the arbitrary state name.
            
            filename = "{0}_correlations_{1}.json".format(year,s_filename) # String for file name
            if not os.path.exists('data/correlations/years/{}'.format(s_filename)):
                os.makedirs('data/correlations/years/{}'.format(s_filename),exist_ok=True)
            with open('data/correlations/years/{0}/{1}'.format(s_filename,filename),'w') as f: # Opens temporary instance of file
                f.write(json.dumps(cor,sort_keys=True)) # Writes data to file
            
if __name__ == "__main__":
    # Import data file. Change all Ds and Ts with 0.
    data = pd.read_csv("em_10yr_data.csv",dtype=str).replace(to_replace=np.NAN,value=0).replace(to_replace="(D)",value=0).replace(to_replace="(L)",value=0).replace(to_replace="(NA)",value=0)

    # Gets list of states
    state_list = list(set(data['GeoName']))
    
    for stat in state_list:
        compare_to_state(stat,state_list)
