import os
from ringcentral import SDK

# PATH PARAMETERS
accountId = '<ENTER VALUE>'
domain = '<ENTER VALUE>'
sourceRecordId = '<ENTER VALUE>'

# OPTIONAL QUERY PARAMETERS
queryParams = {

}

# ENVIRONMENT VARIABLES
rcsdk = SDK(os.environ['RC_CLIENT_ID'], os.environ['RC_CLIENT_SECRET'], os.environ['RC_SERVER_URL'])
platform = rcsdk.platform()
platform.login( jwt=os.environ.get('RC_JWT') )
r = platform.get(f'/ai/ringsense/v1/public/accounts/{accountId}/domains/{domain}/records/{sourceRecordId}/insights', queryParams)
# PROCESS RESPONSE