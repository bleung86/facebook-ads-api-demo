from facebookads import FacebookAdsApi
from facebookads.objects import (
    AdAccount,
    CustomAudience,
    Business,
    Ad,
    AdSet
)
from itertools import islice

import os
import json
import csv


def main():
    
    this_dir = os.path.dirname(__file__)
    config_filename = os.path.join(this_dir, 'config.json') 
    
    ### Setup dummy records
    fileName = 'Test_Records.txt'
    row_num = 2345678
    payload = 10000
    CustomAudience_name = 'Data Engineers'
    CustomAudience_desc = 'Thie is a test'
    
    ### Setup session and api objects
    config_file = open(config_filename)
    config = json.load(config_file)
    config_file.close()
    
    auth_info = (
        config['app_id'],
        config['app_secret'],
        config['access_token'])
    
    session = FacebookAdsApi.init(*auth_info)
    
    ##Setup Custom Audience
    my_account = AdAccount(config['act_id'])
    audience = create_CustomAudience(my_account, CustomAudience_name, CustomAudience_desc)
        
    print_header()
    generate_testfile(fileName, row_num)
    
    user_lists = read_testfile(fileName, payload)
    for user_list in user_lists:
        '''
        ## Need to refactor and add http exception handling
        '''
        audience.add_users(CustomAudience.Schema.email_hash, user_list)
        print(FacebookAdsApi.get_num_requests_attempted(session))
            
    '''
    # Old Codes
    file = open(fileName, 'r')
    with file as f:
        while True:
            user_list = list(islice(f, payload))
            if not user_list:
                break
            audience.add_users(CustomAudience.Schema.email_hash, user_list)
    file.close()  
    '''
def create_CustomAudience(my_account, name, description=None):
    audience = CustomAudience(parent_id=my_account.get_id_assured())
    audience.update({
        CustomAudience.Field.name: name,
        CustomAudience.Field.subtype: CustomAudience.Subtype.custom,
    })
    if description:
        audience.update({CustomAudience.Field.description: description})
    audience.remote_create()
    print('Created custom audience id ' + audience[CustomAudience.Field.id])
    return audience



def print_header():
    print('---------------------------------------------------------')
    print('           FACEBOOK MARKET CUSTOM AUDIENCE               ')
    print('---------------------------------------------------------')
    print()


def generate_testfile(fileName, row_num):
    
    f = open(fileName, 'wt')
    try:
        writer = csv.writer(f, lineterminator='\n')
        for i in range(row_num):
            ##writer.writerow( (chr(ord('a') + i), '08/%02d/07' % (i+1)) )
            writer.writerow(('Test%d@email.com'% (i+1),))
    finally:
        f.close()
        print ('Test File Created')

def read_testfile(fileName, payload):
    """
    Generator to yield one line instead of storing all lines in memory.
    """
    with open(fileName, 'r') as file_in:
        while True:
            user_list = list(islice(file_in, payload))
            if not user_list:
                break
            yield user_list       
    file_in.close() 

def facebook_ads_api_call():
    """ Facebook API functionality goes here.
    """
    pass

if __name__ == '__main__':
    main()
