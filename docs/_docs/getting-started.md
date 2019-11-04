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

{% include alert.html type="info" title="Under Development!" content="Note that there are currently no usable versions pushed to pypi, so you are best to test with installation from source." %}

## Image Specification

The image specification is provided in the `image` module, and can be loaded
as follows:

```python
from opencontainers.image import Image
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
```

If any field is invalid (meaning the wrong type) it will spit out an error at you immediately.
To validate the entire structure (e.g., to ensure that all required fields are provided)
you do this:

```python
image.validate()
```

You can take a look at the [config testing file](https://github.com/vsoch/oci-python/blob/master/opencontainers/tests/test_config.py) for other examples of valid and invalid image configs.


## Image Manifest

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

**under development**
