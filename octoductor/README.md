# Application
This folder contains the octoductor application code. All of the code is deplopyed in a dedicated Lambda layer and can be referenced in functions depending on the layer. Services are implemented as Flask apps and deployed via a tiny WSGI layer on top of them. I.e., the Lambda could be inline code like this:

```python
import serverless_wsgi
import json
from data.api import app
from common import logger

def handler(event, context):
    logger.debug("Received event: " + json.dumps(event))
    return serverless_wsgi.handle_request(app, event, context)
```

## TODO
Decouple the application core from integrations like GitHub / CodeCov...
