# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


# AnnotationCreated is the annotation key for the date and time on which the image was built (date-time string as defined by RFC 3339).
AnnotationCreated = "org.opencontainers.image.created"

# AnnotationAuthors is the annotation key for the contact details of the people or organization responsible for the image (freeform string).
AnnotationAuthors = "org.opencontainers.image.authors"

# AnnotationURL is the annotation key for the URL to find more information on the image.
AnnotationURL = "org.opencontainers.image.url"

# AnnotationDocumentation is the annotation key for the URL to get documentation on the image.
AnnotationDocumentation = "org.opencontainers.image.documentation"

# AnnotationSource is the annotation key for the URL to get source code for building the image.
AnnotationSource = "org.opencontainers.image.source"

# AnnotationVersion is the annotation key for the version of the packaged software.
# The version MAY match a label or tag in the source code repository.
# The version MAY be Semantic versioning-compatible.
AnnotationVersion = "org.opencontainers.image.version"

# AnnotationRevision is the annotation key for the source control revision identifier for the packaged software.
AnnotationRevision = "org.opencontainers.image.revision"

# AnnotationVendor is the annotation key for the name of the distributing entity, organization or individual.
AnnotationVendor = "org.opencontainers.image.vendor"

# AnnotationLicenses is the annotation key for the license(s) under which contained software is distributed as an SPDX License Expression.
AnnotationLicenses = "org.opencontainers.image.licenses"

# AnnotationRefName is the annotation key for the name of the reference for a target.
# SHOULD only be considered valid when on descriptors on `index.json` within image layout.
AnnotationRefName = "org.opencontainers.image.ref.name"

# AnnotationTitle is the annotation key for the human-readable title of the image.
AnnotationTitle = "org.opencontainers.image.title"

# AnnotationDescription is the annotation key for the human-readable description of the software packaged in the image.
AnnotationDescription = "org.opencontainers.image.description"
