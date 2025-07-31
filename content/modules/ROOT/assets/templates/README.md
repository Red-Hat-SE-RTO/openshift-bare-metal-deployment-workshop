# Workshop Templates

This directory contains configuration templates, scripts, and examples that are directly referenced and used in the workshop modules. All templates should be production-ready and thoroughly tested.

## Directory Structure

```
templates/
├── install-configs/     # Installation configuration templates
├── network-configs/     # Network configuration templates  
├── scripts/            # Utility scripts and automation
└── README.md          # This file
```

## Template Categories

### Installation Configuration Templates (`install-configs/`)
- `install-config-assisted.yaml` - Assisted Installer configuration
- `install-config-agent-based.yaml` - Agent-based Installer configuration
- `agent-config-template.yaml` - Agent-based node configuration
- `cluster-config-examples/` - Various cluster configuration examples

### Network Configuration Templates (`network-configs/`)
- `dns-zone-template.txt` - DNS zone file template
- `haproxy-config-template.cfg` - HAProxy load balancer configuration
- `nmstate-examples/` - Nmstate configuration examples
- `network-policy-examples/` - Network policy templates

### Utility Scripts (`scripts/`)
- `verify-hardware.sh` - Hardware requirements verification
- `setup-dns.sh` - DNS configuration automation
- `test-network.sh` - Network connectivity testing
- `validate-cluster.sh` - Post-installation validation

## Template Standards

### File Naming
- Use kebab-case for all file names
- Include version information when relevant
- Use descriptive names indicating purpose and use case
- Examples:
  - `install-config-assisted-4.18.yaml`
  - `network-validation-script.sh`
  - `dns-zone-template.txt`

### Content Standards
Each template must include:

```yaml
# Template: [Template Name]
# Version: OpenShift 4.18/4.19
# Use Case: [Specific use case or scenario]
# Prerequisites: [List of prerequisites]
# Instructions: [How to use this template]
# Documentation: [Link to relevant Red Hat docs]
# Last Updated: [Date]

# Template content here...
```

### Placeholder Conventions
- Use `<PLACEHOLDER_NAME>` for values users must replace
- Use descriptive placeholder names (e.g., `<CLUSTER_NAME>`, not `<NAME>`)
- Include validation criteria in comments
- Provide example values in comments

## Usage in Workshop Modules

### Direct Download Links
```adoc
Download the configuration template:
link:assets/templates/install-configs/install-config-assisted.yaml[install-config.yaml template]
```

### Inline Template Display
```adoc
[source,yaml]
----
include::assets/templates/install-configs/install-config-assisted.yaml[]
----
```

### Script Execution Examples
```adoc
[source,bash]
----
# Download and run the hardware verification script
curl -O {workshop-url}/assets/templates/scripts/verify-hardware.sh
chmod +x verify-hardware.sh
./verify-hardware.sh control-plane
----
```

### Template Customization Instructions
```adoc
== Step 1: Customize Configuration Template

1. Download the template: link:assets/templates/install-configs/install-config-assisted.yaml[install-config.yaml]
2. Replace the following placeholders:
   - `<CLUSTER_NAME>`: Your cluster name (e.g., "my-openshift")
   - `<BASE_DOMAIN>`: Your base domain (e.g., "example.com")
   - `<PULL_SECRET>`: Your Red Hat pull secret

[source,bash]
----
# Validate your configuration
openshift-install create manifests --dir=./cluster-config
----
```

## Example Templates

### Install Config Template
```yaml
# Template: Assisted Installer Configuration
# Version: OpenShift 4.18/4.19
# Use Case: Standard bare metal deployment
# Prerequisites: DNS configured, hardware meets requirements
# Instructions: Replace all <PLACEHOLDER> values
# Documentation: https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/installing_on-premise_with_assisted_installer/installing-on-prem-assisted

apiVersion: v1
baseDomain: <BASE_DOMAIN>  # Example: example.com
metadata:
  name: <CLUSTER_NAME>     # Example: my-openshift-cluster
compute:
- name: worker
  replicas: <WORKER_COUNT> # Example: 3
controlPlane:
  name: master
  replicas: 3              # Always 3 for HA
networking:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  serviceNetwork:
  - 172.30.0.0/16
  machineNetwork:
  - cidr: <MACHINE_NETWORK_CIDR>  # Example: 192.168.1.0/24
platform:
  none: {}
pullSecret: '<PULL_SECRET>'       # From console.redhat.com
sshKey: '<SSH_PUBLIC_KEY>'        # Your SSH public key
```

### Hardware Verification Script
```bash
#!/bin/bash
# Template: Hardware Verification Script
# Version: OpenShift 4.18/4.19
# Use Case: Validate hardware meets OpenShift requirements
# Prerequisites: Run on each node to be added to cluster
# Instructions: ./verify-hardware.sh [control-plane|worker]
# Documentation: https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/installing_on_bare_metal/user-provisioned-infrastructure#minimum-resource-requirements_installing-bare-metal

NODE_TYPE=${1:-worker}

echo "=== OpenShift 4.18/4.19 Hardware Verification ==="
echo "Node Type: $NODE_TYPE"
echo "Node: $(hostname)"
echo "Date: $(date)"
echo

# Verification logic here...
```

## Template Validation

Before using templates in workshop:
- [ ] All placeholders are clearly marked and documented
- [ ] Configuration syntax is valid
- [ ] Scripts execute without errors
- [ ] Templates work with both OpenShift 4.18 and 4.19
- [ ] All prerequisites are documented
- [ ] Links to official documentation are included

## Template Maintenance

### Regular Updates
- Test templates with each OpenShift version update
- Validate against latest Red Hat documentation
- Update comments and documentation links
- Verify script compatibility across different environments

### Version Management
- Maintain separate templates for different OpenShift versions when needed
- Archive outdated templates with clear version labels
- Document breaking changes between versions
- Provide migration guidance for template updates

### Quality Assurance
- Test all scripts in clean environments
- Validate YAML/JSON syntax
- Verify all external dependencies
- Test error handling and edge cases

## Integration with Research

Templates are created based on research findings:

1. **Research Analysis**: Review technical requirements from `research/answers/`
2. **Template Design**: Create templates based on official procedures
3. **Validation**: Test templates against official documentation
4. **Workshop Integration**: Reference templates in appropriate modules
5. **Maintenance**: Update templates when research reveals changes

All templates should be traceable back to official Red Hat documentation and tested procedures.
