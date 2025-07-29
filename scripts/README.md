# Link Checker Scripts

This directory contains scripts for validating links in the OpenShift Bare Metal Workshop documentation.

## Overview

The link checker validates all external links in the workshop documentation to ensure they are accessible and working correctly. It supports both AsciiDoc and Markdown formats and generates detailed reports for any broken links.

## Files

- **`check-links.sh`** - Main link checker script
- **`link-checker-config.json`** - Configuration file for the link checker
- **`README.md`** - This documentation file

## Usage

### Basic Usage

Run the link checker from the project root:

```bash
./scripts/check-links.sh
```

### What It Checks

The script validates links in:
- All `.adoc` files in `content/modules/ROOT/pages/`
- `README.adoc` in the project root

### Link Formats Supported

**AsciiDoc:**
- `link:https://example.com[Link Text]`
- Bare URLs: `https://example.com`

**Markdown:**
- `[Link Text](https://example.com)`
- Bare URLs: `https://example.com`

## Output

### Console Output

The script provides real-time feedback with colored status indicators:
- ✅ **PASS**: Link is accessible
- ❌ **FAIL**: Link is broken or inaccessible
- ⚠️ **WARN**: Link skipped (e.g., requires authentication)
- ℹ️ **INFO**: General information

### Generated Files

1. **`issue.md`** - Detailed report of all link validation results
2. **`link-check.log`** - Complete log of the checking process

### Sample issue.md Report

```markdown
# Link Validation Issues Report

**Generated:** 2024-01-15 10:30:00
**Total Links Checked:** 45
**Failed Links:** 3
**Passed Links:** 42

## ❌ Failed Links (3)

❌ https://broken-link.example.com (in content/modules/ROOT/pages/module-01.adoc)
❌ https://outdated-docs.redhat.com/old-version (in content/modules/ROOT/pages/module-02.adoc)

## 🔧 Recommended Actions

1. Review each failed link and determine if it should be updated, removed, or replaced
2. Common fixes include updating Red Hat documentation links to current versions
3. After making changes, run the link checker again
```

## Configuration

The link checker behavior can be customized via `link-checker-config.json`:

```json
{
  "settings": {
    "timeout": 30,
    "max_redirects": 5,
    "delay_between_checks": 1
  },
  "skip_patterns": [
    "console\\.redhat\\.com.*openshift.*assisted-installer.*clusters$"
  ]
}
```

### Key Configuration Options

- **`timeout`**: Maximum time to wait for each link (seconds)
- **`max_redirects`**: Maximum number of redirects to follow
- **`delay_between_checks`**: Delay between link checks (seconds)
- **`skip_patterns`**: Regex patterns for URLs to skip

## CI/CD Integration

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/link-checker.yml`) that:

- Runs on pushes to main branch
- Runs on pull requests
- Runs weekly to catch external link changes
- Comments on PRs with broken link reports
- Creates issues for broken links found in scheduled runs

### Manual Workflow Trigger

You can manually trigger the link checker workflow in GitHub Actions:

1. Go to the "Actions" tab in your repository
2. Select "Link Checker" workflow
3. Click "Run workflow"

## Troubleshooting

### Common Issues

**Script Permission Denied**
```bash
chmod +x scripts/check-links.sh
```

**Missing Dependencies**
The script requires standard Unix tools:
- `curl` - for HTTP requests
- `grep` - for pattern matching
- `sed` - for text processing

**False Positives**
Some links may fail due to:
- Rate limiting
- Temporary server issues
- Authentication requirements
- Geographic restrictions

### Debugging

Enable verbose logging by checking the generated `link-check.log` file:

```bash
tail -f link-check.log
```

## Best Practices

### For Documentation Authors

1. **Test Links Locally**: Run the link checker before committing changes
2. **Use Stable URLs**: Prefer stable, versioned documentation links
3. **Update Regularly**: Keep links current with latest product versions
4. **Document Skips**: If a link must be skipped, document why in comments

### For Maintainers

1. **Review Reports**: Regularly review generated issue reports
2. **Update Patterns**: Add skip patterns for known problematic URLs
3. **Monitor Trends**: Track link failure patterns over time
4. **Automate Fixes**: Consider automated updates for common patterns

## Examples

### Running with Custom Timeout

Modify the script or configuration to use a longer timeout for slow servers:

```bash
# Edit the timeout value in the script or config file
timeout=60
```

### Checking Specific Files

To check only specific files, modify the script's file discovery logic or create a custom version.

### Integration with Other Tools

The link checker can be integrated with:
- Pre-commit hooks
- Documentation build processes
- Continuous integration pipelines
- Monitoring systems

## Contributing

To improve the link checker:

1. Test changes thoroughly
2. Update this documentation
3. Consider backward compatibility
4. Add appropriate error handling

## Support

For issues with the link checker:

1. Check the generated `link-check.log` for detailed error information
2. Review the `issue.md` report for specific link failures
3. Verify network connectivity and DNS resolution
4. Check if the issue is temporary (server maintenance, etc.)

---

*This link checker is designed specifically for the OpenShift Bare Metal Workshop documentation and follows Red Hat documentation best practices.*
