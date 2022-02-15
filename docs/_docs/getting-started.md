---
title: Getting Started
tags: 
 - jekyll
 - github
description: Getting started with OpenContainers Python
---

# Getting Started

## Install

To install oci-python, you can do so from pypi or the source GitHub repository.

```bash
pip install opencontainers
```
```bash
git clone {{ site.repo }}
cd {{ site.github_repo }}
python setup.py install
```

If you want to use the reggie client, you'll need a few extra dependencies like
requests.

```bash
pip install opencontainers[reggie]
```

## Distribution Specification

While the distribution specification comes with basic classes that might be implemented
by a registry (e.g., repository, tags, and errors):

```bash
$ ls opencontainers/distribution/v1/
error.py  __init__.py  repository.py  tags.py
```

a more common use case is to interact with an existing registry. This is where
we introduce Reggie.

### Reggie

If you are looking for a Python client to interact with an [opencontainers/distribution-spec](https://github.com/opencontainers/distribution-spec) registry, oci-python serves a client, Reggie (python) - "the saint of content management" that 
mimics the official [Reggie client](https://github.com/bloodorangeio/reggie) to interact with an OCI registry.
These sections will show you how to interact with Reggie. You can also look at the test file
[test_distribution.py](https://github.com/vsoch/oci-python/blob/master/opencontainers/tests/test_distribution.py)
that instantiates and uses the client to interact with a [mock server](https://github.com/vsoch/oci-python/blob/master/opencontainers/tests/mock_server.py). If you are looking to implement your own full server in Python,
we direct you to [Django OCI](https://vsoch.github.io/django-oci/).

```python
from opencontainers.distribution.reggie import NewClient
```

Examples of using Reggie follow.

#### Path Substitutions

Reggie supports replacement templates in strings so that the requests look familiar
to what you see defined for the [distrubution-spec](https://github.com/opencontainers/distribution-spec/blob/master/spec.md).
The follow parameters in the table are supported. For some, you can see that they are supported
by multiple functions.

|URI Parameter |Description | Option | Method|
|--------------|------------|--------|-------|
|`<name>`|Namespace of a repository within a registry | WithDefaultName | (Client)| 
|`<name>`|Namespace of a repository within a registry | WithName | (Request)| 
|`<digest>`|Content-addressable identifier| WithDigest|  (Request) |
|`<reference>`|Tag or digest|WithReference| (Request)|
|`<session_id>`|Session ID for upload |WithSessionID | (Request)|


#### Method Chaining

Reggie provides classes for a Client, Request, and a wrapper around a requests.Response.
Under the hood, all of these classes are wrapping the [requests](https://requests.readthedocs.io/en/master/) library.
For the Reggie classes, for example for a Client, several courtesy functions have been created to support
method chaining - or (assuming that we have variables defined) the ability to do something like this:

```python
client = NewClient("http://127.0.0.1:8000")
req = (client.NewRequest("PUT", location).
         SetHeader("Content-Length", configContentLength).
         SetHeader("Content-Type", "application/octet-stream").
         SetQueryParam("digest", configDigest).
         SetBody(configContent))
```

For a RequestClient (which is returned by client.NewRequest()) the following 
functions are available for further chaining to customize the request:

 - SetHeader
 - SetMethod
 - SetUrl
 - SetRetryCallback
 - SetQueryParam
 - SetBody
 - SetAuthToken
 - SetBasicAuth

#### Client Options

When you create a new client, you can provide one or more functions as options. For
example, let's say I want to make a client that has a username and password ready to go,
and in debug mode. I might do:

```python
client = NewClient("http://127.0.0.1:8000",
    WithUsernamePassword("myuser", "mypass"),
    WithDefaultName("myorg/myrepo"),
    WithDebug(True))
```

Notice that there is a comma after the address (the first argument) and each following
argument is a function with some number of inputs. This works because each of the functions 
makes changes to the client instance, and returns "self" or a reference to the class.
In tehe above, the last `WithDebug` function returns the client to the variable `client`.
For the base Client, the following functions are available for chaining.

  - WithUsernamePassword
  - WithAuthScope
  - WithDefaultName
  - WithDebug
  - WithUserAgent

with the exception of NewClient" which returns a new instance of the class. This is done
to ensure that any previously created request objects aren't replaced. For the RequestClient,
the following functions are available for chaining:

  - WithName
  - WithReference
  - WithDigest
  - WithSessionID
  - WithRetryCallback


#### Location Header Parsing

For certain types of requests, such as chunked uploads, the Location header is needed in order to make follow-up requests.
Reggie provides two helper methods to obtain the redirect location. Let's say we have
a request (req) and we hand it to a client to execute:

```python
response = client.Do(req)
```

We can then get the relative or absolute url as follows. Remember that relative doesn't
include the http/https:// part, and absolute does.

```python
print("Relative location: %s" % response.GetRelativeLocation()) # /v2/...
print("Absolute location: %s" % response.GetAbsoluteLocation()) # https://...
```

#### Error Parsing

When you get a response back, you can call the Errors() method that will
attempt to parse the response body into a list of OCI ErrorInfo objects.

```python
for error in response.Errors():
    print(error['code'])
    print(error['message'])
    print(error['detail'])
```

#### HTTP Valid Methods

The following metohds can be handed to a Reggie Python client to issue a request.

```
GET
PUT
PATCH
DELETE
POST
HEAD
OPTIONS
```

#### Custom User-Agent

By default, requests made by Reggie will use a default value for the User-Agent header in order for registry providers to identify incoming requests.

```
client.Config.UserAgent
# 'reggie-python/0.0.11 (https://github.com/vsoch/oci-python)'
```
The version here corresponds to the version of oci-python.

However you can customize this with the client option `WithUserAgent`. Here is an example:

```python
client = NewClient("http://localhost:8000",
    WithUserAgent("my-agent"))

client.Config.UserAgent
# 'my-agent'
```

Next, let's walk through some examples of interacting with a server.


#### 1. Start a server

If you have a registry in mind, great, but if you need to start a development
server we can suggest [django-oci](https://github.com/vsoch/django-oci).
Note that at the time of this writing, django-oci does not have authentication
implemented yet, so push/pull endpoints will work without it.
Here is a quick set of steps to get a server running.

```bash
git clone https://github.com/vsoch/django-oci
cd django-oci

# Install dependencies
python -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install opencontainers

# Database migrations
python manage.py makemigrations
python manage.py makemigrations django_oci
python manage.py migrate
python manage.py runserver
```
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 17, 2020 - 21:53:15
Django version 3.1.2, using settings 'tests.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This should get a development server running! Now you can open another Python
interactive terminal (I like ipython) and test the opencontainers reggie client.

```python
from opencontainers.distribution.reggie import *
client = NewClient("http://127.0.0.1:8000")
```

You can also instantiate the client with a number of options such as authentication,
namespace, and debug mode.

```python
client = NewClient("http://127.0.0.1:8000",
    WithUsernamePassword("myuser", "mypass"),
    WithDefaultName("myorg/myrepo"),
    WithDebug(True))
```
```
client.Config.DefaultName
# 'myorg/myrepo'

client.Config.Debug
# True
```

#### 2. Make Requests

Let's walk through a few basic requests to demonstrate how Reggie Python works, albeit with an empty registry.

##### Upload a blob

Let's walk through creating and uploading a blob to our registry.
First, create the client. This assumes django-oci does not have authentication.

```python
client = NewClient("http://localhost:8000",
           WithDefaultName("myorg/myrepo"),
	   WithDebug(True)
)
```

And then create the request.

```python
# Request an upload session URL
req = client.NewRequest("POST", "/v2/<name>/blobs/uploads/")

req.url
# 'http://localhost:8000/v2/myorg/myrepo/blobs/uploads'

req.method
# 'POST'
```

And do the request. You should get back a 202 response with a "Location" header.

```python
response = client.Do(req)
```

```
response
# <Response [202]>

response.headers['Location']
# '/v2/put/1/session-942e656f-d08f-4df9-a9e4-575eb59aae77/blobs/upload/'
```

You actually don't need to worry about knowing this header, because it will be provided
to the Reggie client with the GetRelativeLocation() function provided with the response object.
Next, let's prepare a blob for an empty manifest config, separated into two chunks "{" and "}."

```bash
blob = "{}"
blobChunk1 = blob[0]
blobChunk2 = blob[1]
```

We also need to provide a range, and calculate a sha256 digest!

```bash
blobChunk1Range = "0-1"
blobChunk2Range = "1-2"
```

Here is a function for the digest calculation:

```
import hashlib
def calculate_digest(content)
    hasher = hashlib.sha256()
    if not isinstance(content, bytes):
        content = content.encode('utf-8')
    hasher.update(content)
    return "sha256:%s" % hasher.hexdigest()
```
```
blobDigest = calculate_digest(blob)
```

Next, let's upload the first chunk.

```python
req = (client.NewRequest("PATCH", response.GetRelativeLocation()).
        SetHeader("Content-Type", "application/octet-stream").
        SetHeader("Content-Length", str(len(blobChunk1))).
        SetHeader("Content-Range", blobChunk1Range).
        SetBody(blobChunk1)
      )
blobResponse = client.Do(req)
```

And upload the final chunk!
```python
req = (client.NewRequest("PATCH", response.GetRelativeLocation()).
        SetHeader("Content-Type", "application/octet-stream").
        SetHeader("Content-Length", str(len(blobChunk2))).
        SetHeader("Content-Range", blobChunk2Range).
        SetBody(blobChunk2)
      )
blobResponse = client.Do(req)
```

Finally, valiate the uploaded blob content.

```python
req = client.NewRequest("GET", "/v2/<name>/blobs/<digest>",
        WithDigest(blobDigest))
response = client.Do(req)
```

##### Upload a Manifest

Let's create a manifest! We will use our previous blob as the config blob.

```python
manifest = {
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": len(blob),
    "digest": blobDigest
  },
  "layers": []
}
```

The manifest isn't "technically valid" because it has no layers, but it will still work
to push to the registry. Now prepare and issue the request to upload the manifest. Notice that we are adding a tag
reference "latest":

```python
req = (client.NewRequest("PUT", "/v2/<name>/manifests/<reference>",
     WithReference("latest")).
     SetHeader("Content-Type", "application/vnd.oci.image.manifest.v1+json").
     SetBody(manifest))
response = client.Do(req)
```

We should see a 201 response!

```python
response.status_code
201
```

Now we can validate the uploaded content.

```python
req = (client.NewRequest("GET", "/v2/<name>/manifests/<reference>",
        WithReference("latest")).
        SetHeader("Accept", "application/vnd.oci.image.manifest.v1+json"))
response = client.Do(req)
```
```python
response.json()
{'schemaVersion': 2,
 'config': {'mediaType': 'application/vnd.oci.image.config.v1+json',
  'size': 2,
  'digest': 'sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a'},
 'layers': []}
```

##### Get A Manifest

As shown above, it's fairly simple to get a manifest.

```python
req = src.NewRequest(
    "GET",
    "/v2/<name>/manifests/<reference>",
    reggie.WithReference("0.1.2dev0"),
)

response = src.Do(req)
manifest = resp.json()
print(manifest)

# The layers, config, and its digest are found here:
layers = manifest["layers"]
config_digest = manifest["config"]["digest"]
```

##### Get A Blob

Let's say that we just retrieved the image config digest via the interaction above,
and we want to further inspect or tweak it. You might do the following to retrieve
the config blob:

```python
def GetBlob(digest):
    req = src.NewRequest("GET", "/v2/<name>/blobs/<digest>", reggie.WithDigest(digest))
    req.stream = True
    return src.Do(req)
```

And then running the function, you could check the status code, act on it,
and return json for the response.

```python
response = GetBlob(digest)
config = response.json()
```

##### Add a Patch

Let's say that you've retrieved the config blob from above, and we did that
so we can get the last working directory of the container. We want
to add a new layer that has a file in that directory.

```python
# Here is the working directory from the config loaded above
working_dir = config["container_config"]["WorkingDir"]
```

Here we are going to write the file to an new .tar.gz.

```python
import tarfile

PATCH_FILE = "patch.tar.gz"
with tarfile.open(PATCH_FILE, mode="w:gz") as tf:
    content = b"A new test file"
    info = tarfile.TarInfo(os.path.join(working_dir, "test.txt"))
    info.size = len(content)
    tf.addfile(info, io.BytesIO(content))
```

And again here is a quick function for calculating the digest and size of this new archive:

```python
import hashlib

def compute_digest(reader):
    m = hashlib.sha256()
    patch_size = 0
    while True:
        data = f.read(64000)
        if not data:
            break
        m.update(data)
        patch_size += len(data)
    patch_digest = "sha256:" + m.hexdigest()
    return patch_digest, patch_size
```

And do the calculating:

```python
with open(PATCH_FILE, "rb") as f:
    patch_digest, patch_size = compute_digest(f)
```

We can now append the new information to our current manifest:

```python
manifest["layers"].append(
    {
        "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
        "size": patch_size,
        "digest": patch_digest,
    }
)
```
Note that the mediaType differs between Docker v2 and oci images.
Then upload the new patch and manifest. 

**todo: need to have discussion about what should be added to reggie vs. shown here**


**Note** this example is provided from [this issue](https://github.com/vsoch/oci-python/issues/15#issuecomment-1035978143)
and thank you to [Tristan](https://github.com/d4l3k)!

##### List Tags

For example, to list all tags for the repo vsoch/django-oci, you might do the following:

```python
req = client.NewRequest("GET", "/v2/<name>/tags/list",
    WithName("vsoch/django-oci"))

req.url
# 'http://127.0.0.1:8000/v2/vsoch/django-oci/tags/list'

req.method
# 'GET'
```

Above, notice that although we've provided a url with `<name>`, the variable is substituted
and we get the full url with `vsoch/django-oci`. Then when we execute the request, we get
a response object.


```python
response = client.Do(req)
```

We get the tags!
```
response
# <Response [200]>

response.json()
# {'name': 'myorg/myrepo', 'tags': ['latest']}
```

##### Auth

As you would expect, Reggie will first try issuing requests without special authentication.
It's up to the registry to return a status code 401 "Authentication is needed" to ask Reggie
to construct a request to authenticate. If you've provided a username and password with `WithUserNamePassword`
then the request can be retried with this added Authorization header. This might look like:

```bash
client = NewClient("http://127.0.0.1:8000",
    WithUsernamePassword("myuser", "mypass"))
```
```
client.Config.Username
# 'myuser'

client.Config.Password
#'mypass'
```

In order for this to work, alongside the 401 response the registry should return a 
Www-Authenticate header that describes how to to authenticate. An example might
include a realm, scope, and service.

```
'realm="https://pizza.com/v2/auth",service="testservice",scope="pull,push"'
```

For more info about the Www-Authenticate header and general HTTP auth topics, please see IETF RFCs [7235](https://tools.ietf.org/html/rfc7235) and [6749](https://tools.ietf.org/html/rfc6749).

**Basic Auth**

If the Www-Authenticate header contains the string "Basic," then the header used in the retried request will be formatted as 
follows:

```
Authorization: Basic <credentials>
```

where credentials is the base64 encoding of the username and password joined by a single colon. E.g.,

```
credentials = myuser:mypass + base64 encoding
```

**"Docker-style" Token Auth**

The more common method used by most commerial registries is "Docker style" token authentication.
If the Www-Authenticate header contains "Bearer" instead, an attempt is made to retrieve
a token from an authorization service. The details of the service are passed to Reggie in the
same header. This authorization endpoint, if the request is valid, will return a token
that is then added to the retried request as follows:

```
Authorization: Bearer <token>
```

**Custom Auth Scope**

If you need to override the scope obtained from the Www-Authenticate header, then you can
set the scope that you need when you instantiate the client:

```python
client = NewClient("http://localhost:8000",
   WithAuthScope("repository:mystuff/myrepo:pull,push"))
```
```
client.Config.AuthScope
'repository:mystuff/myrepo:pull,push'
```

If you find that you want to better develop or improve the current (not used)
Distribution-spec models, please [let us know]({{ site.repo}}/issues).



## Image Specification

### Image

The image specification is provided in the `image` module, and can be loaded
as follows:

```python
from opencontainers.image.v1 import Image
```

When you create a new image structure, it's completely empty.

```python
image = Image()
```

And then a likely use case is to load a json object that follows the image
manifest specification. Here are the minimum required fields:

```python
config_valid_required = {
    "architecture": "amd64",
    "os": "linux",
    "rootfs": {
      "diff_ids": [
        "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"
      ],
      "type": "layers"
    }
}
```

Here is how we would load it. 

```python
image.load(config_valid_required)
<opencontainers.image.v1.config.Image at 0x7fbc87bef400>
```

If any field is invalid (meaning the wrong type) it will spit out an error at you immediately.
To validate the entire structure (e.g., to ensure that all required fields are provided)
you do this:

```python
image.validate()
True
```

You can take a look at the [config testing file](https://github.com/vsoch/oci-python/blob/master/opencontainers/tests/test_config.py) for other examples of valid and invalid image configs.


### Image Manifest

You can import the Image manifest as follows:

```python
from opencontainers.image.v1 import Manifest
```
and instantiate an empty one like this:

```python
manifest = Manifest()
```

Now let's say we have this manifest:

```python
valid_with_optional = {
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "size": 1470,
    "digest": "sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b"
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 675598,
      "digest": "sha256:9d3dd9504c685a304985025df4ed0283e47ac9ffa9bd0326fddf4d59513f0827"
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 156,
      "digest": "sha256:2b689805fbd00b2db1df73fae47562faac1a626d5f61744bfe29946ecff5d73d"
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "size": 148,
      "digest": "sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd"
    }
  ],
  "annotations": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

We would load it into our Manifest like this:

```python
manifest.load(valid_with_optional)
<opencontainers.image.v1.manifest.Manifest at 0x7fbc87a509b0>
```

Loading will check general types (e.g., is the Config MediaType a string?) but
since the MediaType is a general type Descriptor, there can't be a global validation
to check the type of string at this step. To do this detailed validation, meaning
to ensure that:

 - the manifest Config mediaType is correct
 - the manifest Layers mediaTypes are correct

you can run validate as follows:

```python
manifest.validate()
True
```

And you can convert it back into a dictionary:

```python
> manifest.to_dict()
{'schemaVersion': 2,
 'config': {'mediaType': 'application/vnd.oci.image.config.v1+json',
  'digest': 'sha256:c86f7763873b6c0aae22d963bab59b4f5debbed6685761b5951584f6efb0633b',
  'size': 1470},
 'layers': [{'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip',
   'digest': 'sha256:9d3dd9504c685a304985025df4ed0283e47ac9ffa9bd0326fddf4d59513f0827',
   'size': 675598},
  {'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip',
   'digest': 'sha256:2b689805fbd00b2db1df73fae47562faac1a626d5f61744bfe29946ecff5d73d',
   'size': 156},
  {'mediaType': 'application/vnd.oci.image.layer.v1.tar+gzip',
   'digest': 'sha256:c57089565e894899735d458f0fd4bb17a0f1e0df8d72da392b85c9b35ee777cd',
   'size': 148}],
 'annotations': {'key1': 'value1', 'key2': 'value2'}}
```

You can take a look at the [manifest testing file](https://github.com/vsoch/oci-python/blob/master/opencontainers/tests/test_manifest.py) for other examples.

### Descriptor

A descriptor is embedded in image configs and manifests, and likely you won't
interact with it directly, but here is how to do that, just in case.
First, import the class:

```python
from opencontainers.image.v1 import Descriptor
```

Here is a valid descriptor. The types, including the mediaType, the size (int) and
the digest are all important.

```python
valid_descriptor = {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}
```

Let's create the descriptor

```python
desc = Descriptor()
desc.load(valid_descriptor)
<opencontainers.image.v1.descriptor.Descriptor at 0x7fbc879a93c8>
```

Loading also validates, meaning calling the `.validate()` function after all
nested objects are loaded. Speaking of nested objects, you can see them
under attributes:

```python
{'MediaType': <opencontainers.struct.StructAttr-MediaType:application/vnd.oci.image.manifest.v1+json>,
 'Digest': <opencontainers.struct.StructAttr-Digest:sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270>,
 'Size': <opencontainers.struct.StructAttr-Size:7682>,
 'URLs': <opencontainers.struct.StructAttr-URLs:None>,
 'Annotations': <opencontainers.struct.StructAttr-Annotations:None>,
 'Platform': <opencontainers.struct.StructAttr-Platform:None>}
```

It validates because the mediaType, Digest, and Size are all present, and of the correct
formats or nested structures that were also loaded and validated. 

And of course you can dump to json or dictionary if needed.

```python
desc.to_dict()
{'mediaType': 'application/vnd.oci.image.manifest.v1+json',
 'digest': 'sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270',
 'size': 7682}
print(desc.to_json())
{
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
    "size": 7682
}
```

Now here is just one (of many examples) of an invalid descriptor. The mediaType is not
supported.

```python
mediatype_invalidtype = {
    "mediaType": ".foo/bar",
    "size": 7682,
    "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
}
```

Trying to load this will result in an error:

```python
desc.load(mediatype_invalidtype)                                                                                                  
ERROR .foo/bar failed regex validation ^[A-Za-z0-9][A-Za-z0-9!#$&-^_.+]{0,126}/[A-Za-z0-9][A-Za-z0-9!#$&-^_.+]{0,126}$ 
ERROR MediaType (mediaType) is not valid.
```

### Image Index

An image index has a schema version and manifests. Here is an example with optional
attributes like annotations:

```python
index_with_optional = {
    "schemaVersion": 2,
    "manifests": [
        {
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "size": 7143,
            "digest": "sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f",
            "platform": {"architecture": "ppc64le", "os": "linux"},
        },
        {
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "size": 7682,
            "digest": "sha256:5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
            "platform": {"architecture": "amd64", "os": "linux"},
        },
    ],
    "annotations": {"com.example.key1": "value1", "com.example.key2": "value2"},
}
```

We can load it as follows:

```python
from opencontainers.image.v1 import Index
index.load(index_with_optional)                                                                                                  
<opencontainers.image.v1.index.Index at 0x7fbc87aa5d68>
```

And of course an invalid index wouldn't load.


### Image Layout

I'm not sure what these are used for, but here is how to load an image layout.

```python
from opencontainers.image.v1 import ImageLayout
layout = ImageLayout()
```

Here is a valid layout:

```python
layout.load({"imageLayoutVersion": "1.0.0"})
<opencontainers.image.v1.layout.ImageLayout at 0x7fbc87989a58>

layout.attrs                                                                                                                     
{'Version': <opencontainers.struct.StructAttr-Version:1.0.0>}
```

And invalid ones:

```python
layout.load({"imageLayoutVersion": 1.0})
layout.load({"imageLayoutVersion": "1.0"})
```

## Digest

Heavily integrated into most opencontainers structures are digests, which generally
are content identifiers used across the OCI ecosystem. You can read more about
digests <a href="https://github.com/opencontainers/go-digest/#go-digest" target="_blank">here</a>.
Below we will discuss the various classes implemented by OpenContainers Python
to support that.

### Digest

The meaty part of the Digest module is obviously... digests! Let's first
import the class

```python
from opencontainers.digest import Digest
```

Here is likely a common use case, you want to read in some input digest, and 
maybe inspect just the algorithm or the encoded portion:

```python
digest = Digest("sha256:e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b")
digest.algorithm                                                                                                                  
#'sha256'

digest.encoded()                                                                                                                  
#'e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b'
```

Importantly, it validates:

```python
digest.validate()
True
```

This will work for algorithms available (see [Algorithms](#algorithms) below.

#### Invalid Digests

Now let's try loading invalid digests. None of these will validate, they will
throw `ErrDigestInvalidFormat: invalid checksum digest format` errors.

```python
Digest("sha256:").validate()
Digest(":").validate()
Digest("d41d8cd98f00b204e9800998ecf8427e").validate()
```

These will throw `ErrDigestInvalidLength: invalid checksum digest length`. For
the last, the length doesn't match the algorithm chosen.

```python
Digest("sha256:d41d8cd98f00b204e9800m98ecf8427e").validate()
Digest("sha256:abcdef0123456789").validate()
Digest("sha512:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789").validate()
```

These will throw `ErrDigestUnsupported: unsupported digest algorithm`

```python
Digest("foo:d41d8cd98f00b204e9800998ecf8427e").validate()
```

#### Parse

A helper function, "Parse" is provided to return a digest and automatically do
validation.

```python
from opencontainers.digest import Parse

# Passes Validation
digest = Parse("sha256:e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b")
digest.algorithm
# sha256

# Won't be successful, digest unsupported
digest = Parse("foo:d41d8cd98f00b204e9800998ecf8427e")
```

#### New Digest Functions

You can also create a digest from an algorithm, and encoded portion

```python
from opencontainers.digest import NewDigestFromEncoded
alg = Algorithm("sha256")
encoded = e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b
digest = NewDigestFromEncoded(alg, encoded)
# sha256:e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b

digest.validate()
True
```

This would be equal to

```python
parsed = Parse("sha256:e58fcf7418d4390dec8e8fb69d88c06ec07039d651fedd3aa72af9972e7d046b")
parsed == digest
True
```


### Algorithms

Opencontainers Python currently supports the (small set) that are supported
by the GoLang equivalent. You can see all supported by importing the algorithms

```python
from opencontainers.digest.algorithm import algorithms
print(algorithms.keys())
dict_keys(['sha256', 'sha384', 'sha512'])
```

Each algorithm object in the lookup provided is of type Algorithm, a structure
to hold basic parsing functions:

```python
alg = algorithms.get('sha256')
type(alg)
opencontainers.digest.algorithm.Algorithm
```

You could technically instantiate the same object as follows:

```python
from opencontainers.digest import Algorithm
alg = Algorithm('sha256')
```

You can check if the algorithm is available:

```python
alg.available()
True
```

The hashing object is located as alg.hash, for example:

```python
hasher = alg.hash()
hasher.update(b'abc')
hasher.hexdigest()                                                                                                                
'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
```

But most of these interactions are handled via the main Digest class. For example,
you are allowed to load an unsupported type:

```python
alg = Algorithm('shalalala')
alg.available()
False
```

And in this case, the hash() function returns None

```python
hasher = alg.hash()
# hasher is None
```

A simply example below shows generating random bytes, and then showing that
the expected digest is produced using different ways to input the content
to the Algorithm class. First we generate the bytes

```python
import random
import string
asciitext = "".join([random.choice(string.ascii_letters) for n in range(20)])
p = bytes(asciitext, "utf-8")
```

Prepare an algorithm hasher

```python
alg = Algorithm("sha256")
hasher = alg.hash()
hasher.update(p)
```

First, we create a digest with the algorithm and digest:

```python
from opencontainers.digest import Digest
expected = Digest("%s:%s" % (alg, h.hexdigest()))
#  sha256:5670db53addefdd70c99ea28c77f4c84616fe5586689d847a50cf199bad8a810
```

And then we can try producing the same thing using the other Algorithm input
functions, first from a reader:

```python
import io
newReader = io.BytesIO(p)
readerDgst = alg.fromReader(newReader)
readerDgst == expected
True
```

now from bytes:

```python
alg.fromBytes(p) == expected
True
```

and from a string (note we are using the original asciitext)

```python
expected == alg.fromString(asciitext)
True
```

## Distribution Spec

The [distribution-spec](https://github.com/opencontainers/distribution-spec) outlines endpoints and protocol 
(e.g., POST, PUT, PATCH, headers) to interact with an Open Containers registry. Toward this aim, 
the Python module here provides a client, a Python version of [Reggie](https://github.com/bloodorangeio/reggie) to make
it easier to interact with distribution-spec registries.

