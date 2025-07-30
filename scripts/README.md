# Intelligent Link Checker with AI Analysis

## Overview

The Intelligent Link Checker is an enhanced Python-based tool that validates documentation links and provides AI-powered analysis of failures using Red Hat's Granite 3.3 8B Instruct model via LangChain.

## Features

### 🔗 **Advanced Link Validation**
- Robust HTTP client with retry logic and proper headers
- JSON configuration support for flexible settings
- Comprehensive error handling and detailed reporting
- Support for authentication-required URLs (skip patterns)

### 🤖 **AI-Powered Analysis**
- **Pattern Recognition**: Identifies common failure patterns (version mismatches, URL structure changes)
- **Impact Assessment**: Evaluates how broken links affect workshop participants
- **Smart Recommendations**: Provides specific, actionable fix suggestions
- **Alternative Sources**: Suggests working documentation alternatives

### 🐙 **GitHub Integration**
- Automatic GitHub issue creation for broken links
- AI-generated issue titles and descriptions
- Structured issue format with analysis and recommendations
- Proper labeling for easy issue management

## Installation

### Prerequisites
```bash
# Install Python dependencies
pip install -r scripts/requirements.txt
```

### Dependencies
- `requests>=2.31.0` - HTTP client library
- `urllib3>=2.0.0` - HTTP library with retry support
- `langchain>=0.1.0` - LangChain framework
- `langchain-openai>=0.1.0` - OpenAI integration for LangChain
- `langchain-core>=0.1.0` - Core LangChain components

## Usage

### Basic Link Checking
```bash
# Check all modules
python3 scripts/intelligent_link_checker.py

# Check specific files
python3 scripts/intelligent_link_checker.py content/modules/ROOT/pages/module-05-storage.adoc

# Test mode (first 3 links only)
python3 scripts/intelligent_link_checker.py --test-mode

# Limit links per file
python3 scripts/intelligent_link_checker.py --max-links 10
```

### AI Analysis and GitHub Integration
```bash
# Run with AI analysis and create GitHub issue for failures
python3 scripts/intelligent_link_checker.py --create-github-issue --github-repo owner/repo

# Set GitHub token via environment variable
export GITHUB_TOKEN=your_token_here
python3 scripts/intelligent_link_checker.py --create-github-issue
```

## Configuration

### JSON Configuration (`scripts/link-checker-config.json`)
```json
{
  "settings": {
    "timeout": 30,
    "max_redirects": 5,
    "delay_between_checks": 1,
    "user_agent": "Mozilla/5.0 (compatible; OpenShift-Workshop-LinkChecker/1.0)"
  },
  "skip_patterns": [
    "console\\.redhat\\.com.*openshift.*assisted-installer.*clusters$"
  ],
  "skip_reasons": {
    "console\\.redhat\\.com.*openshift.*assisted-installer.*clusters$": "requires authentication"
  },
  "output": {
    "log_file": "link-check.log",
    "issue_file": "issue.md",
    "verbose": true,
    "colors": true
  }
}
```

### AI Model Configuration
The tool uses Red Hat's Granite 3.3 8B Instruct model:
- **Endpoint**: `https://granite-3-3-8b-instruct-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1`
- **Model**: `granite-3-3-8b-instruct`
- **Temperature**: 0.01 (focused, deterministic responses)
- **Max Tokens**: 1024 (sufficient for detailed analysis)

## AI Analysis Capabilities

### Pattern Recognition
The AI analyzes broken links to identify:
- **Version Mismatches**: Links pointing to outdated OpenShift versions
- **URL Structure Changes**: Red Hat documentation restructuring
- **Domain Changes**: Documentation moved to new domains
- **Authentication Issues**: Links requiring login credentials

### Impact Assessment
Evaluates how broken links affect:
- **Workshop Flow**: Disruption to learning progression
- **Participant Experience**: Frustration and confusion
- **Content Authority**: Credibility of workshop materials
- **Maintenance Burden**: Effort required for fixes

### Smart Recommendations
Provides specific actions:
- **Version Updates**: Upgrade to current OpenShift documentation
- **URL Corrections**: Fix typos and structural issues
- **Alternative Sources**: Working documentation alternatives
- **Preventive Measures**: Strategies to avoid future breaks

## GitHub Issue Creation

### Automatic Issue Generation
When broken links are detected, the tool can automatically create GitHub issues with:

**Issue Title**: `🔗 Broken Documentation Links Detected - X failures`

**Issue Content**:
- AI analysis of failure patterns
- Impact assessment on workshop participants
- Specific recommendations for each broken link
- Structured list of all broken links by module
- Next steps for resolution

**Labels**: `documentation`, `bug`, `automated`, `link-checker`

### GitHub Token Setup
```bash
# Set as environment variable
export GITHUB_TOKEN=ghp_your_token_here

# Or pass via command line
python3 scripts/intelligent_link_checker.py --create-github-issue --github-repo owner/repo
```

## CI/CD Integration

### GitHub Actions Workflow
The tool integrates with GitHub Actions for automated link checking:

```yaml
- name: Run intelligent link checker
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python3 scripts/intelligent_link_checker.py --create-github-issue --github-repo ${{ github.repository }}
```

### Workflow Triggers
- **Push to main**: Validate documentation changes
- **Pull Requests**: Check links before merging
- **Scheduled**: Weekly validation to catch external changes
- **Manual**: On-demand validation

## Output Examples

### Console Output
```
2025-07-29 18:19:44,127 - INFO - 🚀 Processing Module 05: Storage
2025-07-29 18:19:44,127 - INFO - 📄 File: content/modules/ROOT/pages/module-05-storage.adoc
2025-07-29 18:19:44,133 - INFO - 🔗 Testing first 3 links (limited for testing)
2025-07-29 18:19:45,841 - INFO - ✅ PASS: https://docs.redhat.com/... (1.71s)
2025-07-29 18:19:52,388 - ERROR - ❌ FAIL: https://docs.redhat.com/... - HTTP 404
2025-07-29 18:19:52,389 - INFO - 🤖 Performing AI analysis of link failures...
2025-07-29 18:19:55,123 - INFO - ✅ AI analysis completed
2025-07-29 18:19:55,456 - INFO - 🐙 Creating GitHub issue...
2025-07-29 18:19:56,789 - INFO - ✅ GitHub issue created: https://github.com/owner/repo/issues/123
```

### Generated Report (`issue.md`)
```markdown
# OpenShift Bare Metal Workshop - Link Validation Report

**Generated:** 2025-07-29 18:19:52
**Total Links Checked:** 26
**Passed Links:** 24
**Failed Links:** 2
**Success Rate:** 92%

## 🤖 AI Analysis

The broken links show a pattern of OpenShift 4.18 documentation URLs returning 404 errors, 
indicating that Red Hat has restructured their documentation. The observability and 
monitoring documentation appears to have moved to a new URL structure...

## 🎯 Recommendations

1. Update all OpenShift 4.18 links to use the current 4.19 documentation structure
2. Replace `/html/observability/` paths with `/html-single/observability/`
3. Verify all Red Hat documentation links use the latest available versions
```

## Troubleshooting

### Common Issues

**LangChain Import Error**
```bash
pip install langchain langchain-openai langchain-core
```

**GitHub API Authentication**
```bash
export GITHUB_TOKEN=your_personal_access_token
```

**AI Model Connection Issues**
- Verify network connectivity to the Granite model endpoint
- Check if the model service is available
- Review model configuration in the script

### Debug Mode
Enable verbose logging by modifying the configuration:
```json
{
  "output": {
    "verbose": true,
    "log_file": "debug-link-check.log"
  }
}
```

## Benefits Over Bash Version

### ✅ **Reliability**
- Proper HTTP client with retry logic
- Better error handling and reporting
- Consistent results across environments

### ✅ **Intelligence**
- AI-powered failure analysis
- Pattern recognition and recommendations
- Impact assessment for broken links

### ✅ **Automation**
- GitHub issue creation
- CI/CD integration
- Structured reporting

### ✅ **Maintainability**
- JSON configuration
- Modular Python code
- Extensible architecture

---
*Enhanced with AI analysis using Red Hat's Granite 3.3 8B Instruct model*
