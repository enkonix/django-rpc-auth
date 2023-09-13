# django-rpc-auth

Django middleware for central auth service based on RPC with [Nameko] microservice framework.

# Installation

Add `'django_rpc_auth'` to your `INSTALLED_APPS` setting.


    INSTALLED_APPS = (
        ...
        'django_rpc_auth',
    )

Replace default `'AuthenticationMiddleware'`:


    MIDDLEWARE = (
        ...
        'django_rpc_auth.middleware.AuthenticationMiddleware',
    )

Run migrations.

# Configuration

```python
SESSION_COOKIE_NAME = 'devsessionid'

NAMEKO_CONFIG = { 
    'AMQP_URI': 'amqp://guest:guest@localhost'
}  
NAMEKO_POOL_SIZE = 4
```
