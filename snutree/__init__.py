from pkg_resources import get_distribution, DistributionNotFound

try:
    version = get_distribution(__name__).version
except DistributionNotFound:
    version = 'unknown'

