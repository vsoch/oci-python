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

