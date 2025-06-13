from .response import Response
from .client import (
    NewClient,
    ClientConfig,
    WithUsernamePassword,
    WithAuthScope,
    WithDefaultName,
    WithDebug,
    WithUserAgent,
    WithProxy,
)
from .request import (
    WithName,
    WithReference,
    WithDigest,
    WithSessionID,
    WithRetryCallback,
)
