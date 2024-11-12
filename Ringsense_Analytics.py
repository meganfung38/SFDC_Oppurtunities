# https://developers.ringcentral.com/my-account.html#/applications
# Find your credentials at the above url, set them as environment variables, or enter them below

# PATH PARAMETERS
accountId = '<ENTER VALUE>'
domain = '<ENTER VALUE>'
sourceRecordId = '<ENTER VALUE>'

# OPTIONAL QUERY PARAMETERS
queryParams = {

}

import os
from ringcentral import SDK
rcsdk = SDK(os.environ['RC_CLIENT_ID'], os.environ['RC_CLIENT_SECRET'], os.environ['RC_SERVER_URL'])
platform = rcsdk.platform()
platform.login( jwt=os.environ.get('RC_JWT') )
r = platform.get(f'/ai/ringsense/v1/public/accounts/{accountId}/domains/{domain}/records/{sourceRecordId}/insights', queryParams)
# PROCESS RESPONSE