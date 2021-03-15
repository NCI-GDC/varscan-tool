try:
    from varscan_tool._version import __long_version__

    __version__ = __long_version__
except ImportError:
    __version__ = "0.0.0"
