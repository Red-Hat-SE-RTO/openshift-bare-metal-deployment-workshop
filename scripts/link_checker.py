#!/usr/bin/env python3
"""
OpenShift Bare Metal Workshop - Python Link Checker
A robust link validation tool with JSON configuration support.
"""

import json
import re
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

@dataclass
class LinkResult:
    """Data class for link validation results."""
    url: str
    status_code: Optional[int]
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    response_time: float
    error_message: Optional[str] = None
    final_url: Optional[str] = None  # After redirects

@dataclass
class ModuleResult:
    """Data class for module validation results."""
    module_name: str
    file_path: str
    total_links: int
    passed_links: int
    failed_links: int
    skipped_links: int
    links: List[LinkResult]
    processing_time: float

class LinkChecker:
    """Main link checker class with JSON configuration support."""
    
    def __init__(self, config_file: str = "scripts/link-checker-config.json"):
        """Initialize the link checker with configuration."""
        self.config = self._load_config(config_file)
        self.session = self._create_session()
        self.logger = self._setup_logging()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration if file doesn't exist
            return {
                "settings": {
                    "timeout": 30,
                    "max_redirects": 5,
                    "delay_between_checks": 1,
                    "user_agent": "Mozilla/5.0 (compatible; OpenShift-Workshop-LinkChecker/1.0)"
                },
                "skip_patterns": [
                    r"console\.redhat\.com.*openshift.*assisted-installer.*clusters$"
                ],
                "skip_reasons": {
                    r"console\.redhat\.com.*openshift.*assisted-installer.*clusters$": "requires authentication"
                },
                "file_patterns": {
                    "adoc": {
                        "extensions": [".adoc"],
                        "link_patterns": [
                            r"link:(https?://[^[]+)\[",
                            r"(https?://[^\s\[\]<>()]+)"
                        ]
                    }
                },
                "output": {
                    "log_file": "link-check.log",
                    "issue_file": "issue.md",
                    "verbose": True,
                    "colors": True
                }
            }
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': self.config['settings']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('LinkChecker')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = self.config['output']['log_file']
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def extract_links_from_file(self, file_path: str) -> List[str]:
        """Extract links from an AsciiDoc file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return []
        
        links = set()
        
        # Extract AsciiDoc link:URL[text] format
        link_pattern = r"link:(https?://[^[]+)\["
        for match in re.finditer(link_pattern, content):
            links.add(match.group(1))
        
        # Extract bare URLs
        url_pattern = r"(https?://[^\s\[\]<>()]+)"
        for match in re.finditer(url_pattern, content):
            url = match.group(1)
            # Skip if it's already captured by link: pattern
            if not re.search(r"link:" + re.escape(url), content):
                links.add(url)
        
        return sorted(list(links))
    
    def should_skip_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Check if URL should be skipped based on patterns."""
        for pattern in self.config['skip_patterns']:
            if re.search(pattern, url):
                reason = self.config['skip_reasons'].get(pattern, "configured to skip")
                return True, reason
        return False, None
    
    def check_url(self, url: str) -> LinkResult:
        """Check a single URL and return result."""
        start_time = time.time()
        
        # Check if URL should be skipped
        should_skip, skip_reason = self.should_skip_url(url)
        if should_skip:
            return LinkResult(
                url=url,
                status_code=None,
                status='SKIP',
                response_time=time.time() - start_time,
                error_message=skip_reason
            )
        
        try:
            response = self.session.get(
                url,
                timeout=self.config['settings']['timeout'],
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            
            if response.status_code in [200, 201, 202, 203, 204, 205, 206, 300, 301, 302, 303, 304, 307, 308]:
                status = 'PASS'
                error_message = None
            else:
                status = 'FAIL'
                error_message = f"HTTP {response.status_code}"
            
            return LinkResult(
                url=url,
                status_code=response.status_code,
                status=status,
                response_time=response_time,
                error_message=error_message,
                final_url=response.url if response.url != url else None
            )
            
        except requests.exceptions.Timeout:
            return LinkResult(
                url=url,
                status_code=None,
                status='FAIL',
                response_time=time.time() - start_time,
                error_message="Request timeout"
            )
        except requests.exceptions.ConnectionError:
            return LinkResult(
                url=url,
                status_code=None,
                status='FAIL',
                response_time=time.time() - start_time,
                error_message="Connection error"
            )
        except Exception as e:
            return LinkResult(
                url=url,
                status_code=None,
                status='ERROR',
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def get_module_name(self, file_path: str) -> str:
        """Extract module name from file path."""
        filename = Path(file_path).name
        
        # Extract module name from filename
        match = re.match(r'^module-(\d+)-(.+)\.adoc$', filename)
        if match:
            module_num = match.group(1)
            module_desc = match.group(2).replace('-', ' ').title()
            return f"Module {module_num}: {module_desc}"
        elif filename == "README.adoc":
            return "README Documentation"
        else:
            return Path(file_path).stem.title()
    
    def check_module(self, file_path: str, max_links: Optional[int] = None) -> ModuleResult:
        """Check all links in a module file."""
        start_time = time.time()
        module_name = self.get_module_name(file_path)
        
        self.logger.info(f"🚀 Processing {module_name}")
        self.logger.info(f"📄 File: {file_path}")
        
        # Extract links
        links = self.extract_links_from_file(file_path)
        
        if not links:
            self.logger.info(f"No links found in {module_name}")
            return ModuleResult(
                module_name=module_name,
                file_path=file_path,
                total_links=0,
                passed_links=0,
                failed_links=0,
                skipped_links=0,
                links=[],
                processing_time=time.time() - start_time
            )
        
        # Limit links if specified (for testing)
        if max_links:
            links = links[:max_links]
            self.logger.info(f"🔗 Testing first {len(links)} links (limited for testing)")
        else:
            self.logger.info(f"🔗 Found {len(links)} links to validate")
        
        # Check each link
        results = []
        for i, url in enumerate(links, 1):
            self.logger.info(f"[{i}/{len(links)}] Checking: {url}")
            
            result = self.check_url(url)
            results.append(result)
            
            # Log result
            if result.status == 'PASS':
                self.logger.info(f"✅ PASS: {url} ({result.response_time:.2f}s)")
            elif result.status == 'SKIP':
                self.logger.info(f"⚠️ SKIP: {url} - {result.error_message}")
            elif result.status == 'FAIL':
                self.logger.error(f"❌ FAIL: {url} - {result.error_message}")
            else:
                self.logger.error(f"🔥 ERROR: {url} - {result.error_message}")
            
            # Respectful delay between requests
            if i < len(links):
                time.sleep(self.config['settings']['delay_between_checks'])
        
        # Calculate statistics
        passed = sum(1 for r in results if r.status == 'PASS')
        failed = sum(1 for r in results if r.status == 'FAIL')
        skipped = sum(1 for r in results if r.status == 'SKIP')
        
        processing_time = time.time() - start_time
        
        # Log module summary
        if failed == 0:
            self.logger.info(f"✅ {module_name}: ALL LINKS WORKING ({passed} passed, {skipped} skipped)")
        else:
            self.logger.error(f"❌ {module_name}: {failed} LINKS FAILED ({passed} passed, {skipped} skipped)")
        
        return ModuleResult(
            module_name=module_name,
            file_path=file_path,
            total_links=len(results),
            passed_links=passed,
            failed_links=failed,
            skipped_links=skipped,
            links=results,
            processing_time=processing_time
        )
    
    def generate_report(self, results: List[ModuleResult]) -> None:
        """Generate markdown report from results."""
        report_file = self.config['output']['issue_file']
        
        # Calculate totals
        total_links = sum(r.total_links for r in results)
        total_passed = sum(r.passed_links for r in results)
        total_failed = sum(r.failed_links for r in results)
        total_skipped = sum(r.skipped_links for r in results)
        
        with open(report_file, 'w') as f:
            f.write("# OpenShift Bare Metal Workshop - Link Validation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Links Checked:** {total_links}\n")
            f.write(f"**Passed Links:** {total_passed}\n")
            f.write(f"**Failed Links:** {total_failed}\n")
            f.write(f"**Skipped Links:** {total_skipped}\n")
            f.write(f"**Success Rate:** {(total_passed * 100 // total_links) if total_links > 0 else 0}%\n\n")
            
            # Module summaries
            f.write("## Module Summary\n\n")
            for result in results:
                status_icon = "✅" if result.failed_links == 0 else "❌"
                f.write(f"- {status_icon} **{result.module_name}**: ")
                f.write(f"{result.total_links} links ({result.passed_links} passed, ")
                f.write(f"{result.failed_links} failed, {result.skipped_links} skipped)\n")
            
            # Failed links details
            if total_failed > 0:
                f.write(f"\n## ❌ Failed Links ({total_failed})\n\n")
                for result in results:
                    failed_links = [link for link in result.links if link.status == 'FAIL']
                    if failed_links:
                        f.write(f"### {result.module_name}\n\n")
                        for link in failed_links:
                            f.write(f"- ❌ {link.url}\n")
                            f.write(f"  - **Error**: {link.error_message}\n")
                            if link.status_code:
                                f.write(f"  - **Status Code**: {link.status_code}\n")
                            f.write(f"  - **Response Time**: {link.response_time:.2f}s\n\n")
            
            f.write("\n---\n")
            f.write("*Report generated by OpenShift Workshop Python Link Checker*\n")
        
        self.logger.info(f"📋 Report generated: {report_file}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description='OpenShift Workshop Link Checker')
    parser.add_argument('files', nargs='*', help='Files to check (default: all modules)')
    parser.add_argument('--config', default='scripts/link-checker-config.json',
                       help='Configuration file path')
    parser.add_argument('--test-mode', action='store_true',
                       help='Test mode: check only first 3 links per file')
    parser.add_argument('--max-links', type=int,
                       help='Maximum number of links to check per file')

    args = parser.parse_args()
    
    # Initialize checker
    checker = LinkChecker(args.config)
    
    # Determine files to check
    if args.files:
        files_to_check = args.files
    else:
        # Default: all module files
        content_dir = Path("content/modules/ROOT/pages")
        files_to_check = list(content_dir.glob("module-*.adoc"))
        readme_file = Path("README.adoc")
        if readme_file.exists():
            files_to_check.append(readme_file)
    
    # Check files
    results = []
    max_links = 3 if args.test_mode else args.max_links
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            result = checker.check_module(str(file_path), max_links)
            results.append(result)
        else:
            checker.logger.error(f"File not found: {file_path}")
    
    # Generate report
    if results:
        checker.generate_report(results)
        
        # Exit with error code if any links failed
        total_failed = sum(r.failed_links for r in results)
        if total_failed > 0:
            checker.logger.error(f"❌ Link validation completed with {total_failed} failures")
            sys.exit(1)
        else:
            checker.logger.info("🎉 All links are working correctly!")
            sys.exit(0)
    else:
        checker.logger.error("No files processed")
        sys.exit(1)

if __name__ == "__main__":
    main()
