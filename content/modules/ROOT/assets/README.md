# Workshop Assets

This directory contains all assets that need to be accessible from the workshop content, including diagrams, templates, and downloadable resources.

## Directory Structure

```
content/modules/ROOT/assets/
├── README.md                    # This file
├── diagrams/                    # Technical diagrams for workshop
│   ├── architecture/            # System architecture diagrams
│   ├── network/                # Network topology diagrams
│   ├── installation-flows/     # Installation process flows
│   └── README.md
├── templates/                   # Configuration templates and scripts
│   ├── install-configs/        # Installation configuration templates
│   ├── network-configs/        # Network configuration templates
│   ├── scripts/                # Utility scripts and automation
│   └── README.md
└── downloads/                   # Downloadable files and resources
    ├── checklists/             # Printable checklists
    ├── worksheets/             # Planning worksheets
    └── README.md
```

## Asset Usage in Workshop Content

### Diagrams
Reference diagrams in workshop modules using:

```adoc
.OpenShift 4.18 Cluster Architecture
image::diagrams/architecture/openshift-cluster-overview.svg[OpenShift Cluster Architecture,800,600]
```

### Templates
Link to templates for download or copy-paste:

```adoc
Download the configuration template: link:assets/templates/install-configs/install-config-assisted.yaml[install-config.yaml template]
```

### Scripts
Reference scripts that users can download and execute:

```adoc
[source,bash]
----
# Download and run the hardware verification script
curl -O {workshop-url}/assets/templates/scripts/verify-hardware.sh
chmod +x verify-hardware.sh
./verify-hardware.sh control-plane
----
```

## Asset Management

### File Naming Conventions
- Use kebab-case for all file names
- Include version information when relevant
- Use descriptive names that indicate purpose
- Examples:
  - `openshift-4.18-cluster-architecture.svg`
  - `install-config-assisted-template.yaml`
  - `network-validation-script.sh`

### Content Standards
- All assets should be referenced from workshop content
- Include proper attribution and source information
- Maintain version compatibility with OpenShift 4.18/4.19
- Test all scripts and validate all templates

### Maintenance
- Update assets when workshop content changes
- Verify all links and references work correctly
- Archive outdated assets rather than deleting them
- Document changes in commit messages

## Integration with Research

Assets in this directory are created based on research findings:

1. **Research Phase**: Questions answered in `research/answers/`
2. **Asset Creation**: Diagrams and templates created based on research
3. **Content Integration**: Assets referenced in workshop modules
4. **Validation**: Assets tested and validated for accuracy

This ensures all workshop assets are backed by authoritative research and official Red Hat documentation.
