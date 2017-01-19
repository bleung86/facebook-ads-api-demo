from facebookads import FacebookAdsApi
from facebookads.exceptions import FacebookRequestError
from facebookads.objects import (
    AdAccount,
    CustomAudience,
 ##   Business,
 ##   Ad,
 ##   AdSet
)
from itertools import islice

import os
import json
import csv
import sys


def main():
    
    ## Print Header
    print_header()
    
    this_dir = os.path.dirname(__file__)
    config_filename = os.path.join(this_dir, 'config.json') 
    
    #Facebook API max payload per http request - only 10,000 users could be uploaded at a time to a custom audience
    payload = 10000
    
    ### Setup dummy records - needs to be refactored once the custom audience and user list input logic are defined
    fileName = 'Test_Records.txt'
    row_num = 56789
    generate_test_file(fileName, row_num)
    
    ### Setup dummy Custom Audience
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
    
    ## Setup Custom Audience
    my_account = AdAccount(config['act_id'])
    audience = create_custom_audience(my_account, CustomAudience_name, CustomAudience_desc)
       
    ## Data Validation Variables 
    num_lines = sum(1 for line in open(fileName))
    user_list_total = 0
    num_received = 0
    
    ## API Push
    user_list = read_test_file(fileName, payload)
    for users in user_list:
        try:
            user_list_total += len(users)
            r = load_custom_audience(audience, users)
            dataset = json.loads(r._body)
            num_received += dataset['num_received']
            if(session.get_num_requests_attempted() != session.get_num_requests_succeeded()):
                print('One of the requests failed')
                print('Requests Attempted : ')
                print(session.get_num_requests_attempted())
                print('Requests Succeeded : ')
                print(session.get_num_requests_succeeded())
                delete_custom_audience(audience.get_id())
                sys.exit("Load Failed")
        except FacebookRequestError as error:
                print('HTTP Status : ')
                print(error.http_status())
                print('Error Code : ')
                print(error.api_error_code())
                print('Error Message : ')
                print(error.api_error_message())
                delete_custom_audience(audience.get_id())
                sys.exit("Load Failed")
                
    ## Data Validation
    if (num_received != num_lines):
        delete_custom_audience(audience.get_id())
        sys.exit("Load Failed - Records Missing")
    print('----------------------')
    print ('Total Records Listed : ')
    print (num_lines)
    print ('Total Records Loaded : ')
    print (num_received)
    print ('Custom Audience Upload Complete')
    
def create_custom_audience(my_account, name, description=None):
    audience = CustomAudience(parent_id=my_account.get_id_assured())
    audience.update({
        CustomAudience.Field.name: name,
        CustomAudience.Field.subtype: CustomAudience.Subtype.custom
    })
    if description:
        audience.update({CustomAudience.Field.description: description})
    audience.remote_create()
    print('Created custom audience id ' + audience[CustomAudience.Field.id])
    return audience

def load_custom_audience(audience, users, datatype='email', schema=None, app_ids=None):
    if datatype == 'email':
        schema = CustomAudience.Schema.email_hash
    elif datatype == 'phone':
        schema = CustomAudience.Schema.phone_hash
    elif datatype == 'mobile_id':
        schema = CustomAudience.Schema.mobile_advertiser_id
    elif datatype == 'uid':
        schema = CustomAudience.Schema.uid
    else:
        sys.exit("[ERROR] invalid datatype " + datatype)
    r = audience.add_users(schema, users)
    print('Adding users to audience using ' + str(schema))
    return r
    
def delete_custom_audience(audience_id):
    audience = CustomAudience(audience_id)
    print('Deleting audience id ' + audience[CustomAudience.Field.id])
    return audience.remote_delete()

def print_header():
    print('---------------------------------------------------------')
    print('           FACEBOOK MARKET CUSTOM AUDIENCE               ')
    print('---------------------------------------------------------')
    print()

def generate_test_file(fileName, row_num):
    
    f = open(fileName, 'wt')
    writer = csv.writer(f, lineterminator='\n')
    for i in range(row_num):
        writer.writerow(('Test%d@email.com'% (i+1),))
    f.close()
    print ('Test File Created')

def read_test_file(fileName, payload):
    """
    Generator to yield a list of specified number of elements (payload) instead of storing the entire list in memory.
    """
    with open(fileName, 'r') as file_in:
        while True:
            user_list = list(islice(file_in, payload))
            if not user_list:
                break
            yield user_list

if __name__ == '__main__':
    main()
