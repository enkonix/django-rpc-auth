import queue
import weakref
from threading import Lock

from nameko.standalone.rpc import ClusterRpcProxy
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ClusterRpcProxyPool:
    """
    Connection pool for Nameko RPC cluster.
    Pool size can be customized by passing `pool_size` kwarg to constructor.
    Default size is 4.
    *Usage*
        pool = ClusterRpcProxyPool(config)
        pool.start()
        # ...
        with pool.next() as rpc:
            rpc.mailer.send_mail(foo='bar')
        # ...
        pool.stop()
    This class is thread-safe and designed to work with GEvent.
    """
    class RpcContext(object):
        def __init__(self, _pool, config, timeout=None):
            self.pool = weakref.proxy(_pool)
            self.proxy = ClusterRpcProxy(config, timeout=timeout)
            self.rpc = self.proxy.start()

        def stop(self):
            self.proxy.stop()
            self.proxy = None
            self.rpc = None

        def __enter__(self):
            return self.rpc

        def __exit__(self, *args, **kwargs):
            try:
                # noinspection PyProtectedMember
                self.pool._put_back(self)
            except ReferenceError:
                self.stop()

    def __init__(self, config, pool_size=None):
        if pool_size is None:
            pool_size = getattr(settings, 'NAMEKO_POOL_SIZE', 4)
        self.timeout = getattr(settings, 'NAMEKO_TIMEOUT', None)
        self.config = config
        self.pool_size = pool_size
        self.queue = None

    def start(self):
        """
        Populate pool with connections.
        """
        self.queue = queue.Queue()
        for _ in range(self.pool_size):
            ctx = ClusterRpcProxyPool.RpcContext(self, self.config, timeout=self.timeout)
            self.queue.put(ctx)

    def next(self, timeout=False):
        """
        Fetch next connection.
        This method is thread-safe.
        """
        return self.queue.get(timeout=timeout)

    def _put_back(self, ctx):
        self.queue.put(ctx)

    def stop(self):
        """
        Stop queue and remove all connections from pool.
        """
        while True:
            try:
                ctx = self.queue.get_nowait()
                ctx.stop()
            except queue.Empty:
                break
        self.queue.queue.clear()
        self.queue = None


pool = None
create_pool_lock = Lock()


def get_pool():
    """
    Use this method to acquire connection pool.
    Example usage:
        from coreservices.core.rpc import get_pool
        # ...
        with get_pool().next() as rpc:
            rpc.mailer.send_mail(foo='bar')
    """
    create_pool_lock.acquire()
    global pool
    if not pool:
        # Lazy instantiation
        if not hasattr(settings, 'NAMEKO_CONFIG') or not settings.NAMEKO_CONFIG:
            raise ImproperlyConfigured('NAMEKO_CONFIG must be specified and should include at least "AMQP_URI" key.')
        pool = ClusterRpcProxyPool(settings.NAMEKO_CONFIG)
        pool.start()
    create_pool_lock.release()
    return pool


def destroy_pool():
    global pool
    pool = None
