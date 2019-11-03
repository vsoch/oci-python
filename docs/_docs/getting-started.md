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


**under development**
