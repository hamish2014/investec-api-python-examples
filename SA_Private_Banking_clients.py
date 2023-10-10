'''
As per https://developer.investec.com/za/api-products/documentation/SA_PB_Account_Information
'''
import requests
import json
import os
import base64

sandbox = True
verbose = False
if sandbox:
    host = "https://openapisandbox.investec.com" # for auth token
    client_id = 'yAxzQRFX97vOcyQAwluEU6H6ePxMA5eY'
    secret = '4dY0PjEYqoBrZ99r'
    x_api_key = "eUF4elFSRlg5N3ZPY3lRQXdsdUVVNkg2ZVB4TUE1ZVk6YVc1MlpYTjBaV010ZW1FdGNHSXRZV05qYjNWdWRITXRjMkZ1WkdKdmVBPT0="
    # the x_api_key grants permissions
else:
    host = "https://openapi.investec.com"


print("obtaining oauth2 authentication:")
response = requests.post(
    url = host + '/identity/v2/oauth2/token',
    headers ={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": base64.b64encode( b'%s:%s' % (client_id.encode('utf8'), secret.encode('utf8')) ),
        "x-api-key": x_api_key,
    },
    data = {"grant_type": "client_credentials"},
)
if response.status_code != 200:
    raise ValueError("oauth2 authentication failed (response reason %s). Are you sure the credentials are correct?" % response.reason)
else:
    print("oauth2 authentication successful:")
#print(response)
access_token = json.loads(response.text).get("access_token")
expires_in = response.json().get("expires_in")
print(f" - access_token {access_token}")
print(f" - expires_in {expires_in}")


print('')
print('Get Accounts')
response = requests.get(
    url = host + '/za/pb/v1/accounts',
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    accounts = json.loads(response.text)
    print(' - %s accounts returned' % len(accounts["data"]["accounts"]))
    if verbose:
        print( json.dumps(accounts, sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"{response.status_code} {response.reason} {response.text}")


print('')
print('Get Account Balance')
accountId = accounts["data"]["accounts"][0]["accountId"]
response = requests.get(
    url = f"{host}/za/pb/v1/accounts/{accountId}/balance",
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    account_balance = json.loads(response.text)
    print(" - %s account_balance['data']" % accountId )
    print( json.dumps(account_balance['data'], sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"{response.status_code} {response.reason} {response.text}")


print('')
print('Get Account Transactions')
fromDate= '2021-05-01'
toDate='2023-07-29'
response = requests.get(
    url = f"{host}/za/pb/v1/accounts/{accountId}/transactions?fromDate={fromDate}&toDate={toDate}",
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    transactions = json.loads(response.text)
    print(' - %i transactions between %s and %s' % (len( transactions["data"]["transactions"] ), fromDate, toDate ))
    #print( json.dumps(transactions, sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"transactions query failed {response.status_code} {response.reason} {response.text}")
transactionType='FeesAndInterest'
response = requests.get(
    url = f"{host}/za/pb/v1/accounts/{accountId}/transactions?fromDate={fromDate}&toDate={toDate}&transactionType={transactionType}",
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    transactions = json.loads(response.text)
    print(' - %i fees and interest transactions between %s and %s' % (len( transactions["data"]["transactions"] ), fromDate, toDate ))
    if verbose:
        print( json.dumps(transactions["data"]["transactions"][0], sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"transactions query failed {response.status_code} {response.reason} {response.text}")


print('')
print('Get Beneficiaries')
response = requests.get(
    url = host + '/za/pb/v1/accounts/beneficiaries',
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    beneficiaries = json.loads(response.text)
    print(' - %s beneficiaries returned' % len(beneficiaries["data"]))
    if verbose:
        print( json.dumps(beneficiaries, sort_keys=True, indent=2) )
    else:
        print('beneficiaries["data"][0]:')
        print( json.dumps(beneficiaries["data"][0], sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"{response.status_code} {response.reason} {response.text}")


print('')
print('Get Beneficiary Categories')
response = requests.get(
    url = host + '/za/pb/v1/accounts/beneficiarycategories',
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    }
)
if response.status_code == 200:
    beneficiaries_categories = json.loads(response.text)
    print(' - %s beneficiaries_categories  returned' % len(beneficiaries_categories["data"]))
    print( json.dumps(beneficiaries_categories["data"], sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"{response.status_code} {response.reason} {response.text}")


print('')
print('Transfer Multiple v2')
response = requests.post(
    url = host + '/za/pb/v1/accounts/%s/transfermultiple' % accounts["data"]["accounts"][0]["accountId"],
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    },
    json = {
        'transferList': [
            {
                'beneficiaryAccountId': accounts["data"]["accounts"][1]["accountId"],
                'amount': '42',
                'myReference': 'API transfer',
                'theirReference': 'API transfer'
            }
        ]
    }
)
if response.status_code == 200:
    transfer_response = json.loads(response.text)
    print(' - R42 transferred from accounts[0] to accounts[1]')
    if verbose or True:
        print(json.dumps(transfer_response, sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"POST to {response.url} failed: {response.status_code} {response.reason} {response.text}")


print('')
print('Pay Multiple')
response = requests.post(
    url = host + '/za/pb/v1/accounts/%s/paymultiple' % accounts["data"]["accounts"][0]["accountId"],
    headers = {
        'Authorization': 'Bearer %s' % access_token,
    },
    json = {
        'paymentList': [
            {
                'beneficiaryId': beneficiaries["data"][0]["beneficiaryId"],
                'amount': '28',
                'myReference': 'My 42 payment',
                'theirReference': 'payment 42'
            }
        ]
    }
)
if response.status_code == 200:
    pay_response = json.loads(response.text)
    print(' - R28 paid from accounts[0] to beneficiaries[0]')
    if verbose or True:
        print(json.dumps(pay_response, sort_keys=True, indent=2) )
else:
    raise RuntimeError( f"POST to {response.url} failed: {response.status_code} {response.reason} {response.text}")
