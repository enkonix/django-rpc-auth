from setuptools import find_packages, setup

setup(
    name='django-rpc-auth',
    version='0.1',
    description='Django middleware for central auth service based on RPC with nameko microservice framework.',
    url='https://@bitbucket.org/enkonix/django-rpc-auth.git',
    author='Vitaliy Volkov',
    author_email='v.volkov@enkonix.com',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'django',
        'channels',
        'nameko'
    ]
)
