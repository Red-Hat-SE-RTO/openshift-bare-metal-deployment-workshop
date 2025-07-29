#!/usr/bin/env python3
"""
OpenShift Bare Metal Workshop - Intelligent Link Checker with LangChain
Enhanced link validation with AI-powered analysis and GitHub issue creation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import requests

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    # Fallback: manually load .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Import the base link checker
from link_checker import LinkChecker, ModuleResult, LinkResult

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available. Install with: pip install langchain langchain-openai")

# LangChain search tools
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    SEARCH_AVAILABLE = True
except ImportError:
    try:
        # Alternative import for newer versions
        from langchain.tools import DuckDuckGoSearchRun
        from langchain.utilities import DuckDuckGoSearchAPIWrapper
        SEARCH_AVAILABLE = True
    except ImportError:
        SEARCH_AVAILABLE = False
        print("Warning: LangChain search tools not available. Install with: pip install langchain-community")

@dataclass
class ValidatedReplacement:
    """Validated replacement URL found through web search."""
    original_url: str
    replacement_url: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    validation_method: str
    description: str

@dataclass
class IntelligentAnalysis:
    """AI analysis of link failures."""
    broken_links: List[str]
    analysis: str
    recommendations: List[str]
    impact_assessment: str
    github_issue_title: str
    github_issue_body: str
    validated_replacements: List[ValidatedReplacement]

class IntelligentLinkChecker(LinkChecker):
    """Enhanced link checker with AI analysis capabilities."""
    
    def __init__(self, config_file: str = "scripts/link-checker-config.json"):
        super().__init__(config_file)
        self.ai_enabled = LANGCHAIN_AVAILABLE and self._setup_ai()
        self.search_enabled = SEARCH_AVAILABLE and self._setup_search()
        
    def _setup_ai(self) -> bool:
        """Set up the AI model for analysis."""
        try:
            # Get API key from environment
            mass_api_key = os.getenv('MASS_API')
            if not mass_api_key:
                self.logger.warning("MASS_API not found in environment variables")
                return False

            # Configure the Granite model with proper authentication
            self.llm = ChatOpenAI(
                openai_api_key=mass_api_key,
                openai_api_base="https://granite-3-3-8b-instruct-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1",
                model_name="granite-3-3-8b-instruct",
                temperature=0.01,
                max_tokens=1024,
                streaming=False,  # Disable streaming for analysis
                top_p=0.9,
                presence_penalty=0.5
                # Note: stream_options removed as it's only valid when streaming=True
            )
            
            # Create analysis prompt template
            self.analysis_template = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    """You are an expert technical documentation analyst specializing in Red Hat OpenShift documentation.
                    Your role is to analyze broken documentation links and provide actionable insights.
                    
                    Focus on:
                    1. Identifying patterns in broken links (version mismatches, URL structure changes, etc.)
                    2. Assessing the impact on workshop participants
                    3. Providing specific, actionable recommendations for fixes
                    4. Suggesting alternative documentation sources when appropriate
                    
                    Be concise, technical, and practical in your analysis.
                    """
                ),
                HumanMessagePromptTemplate.from_template("{input}"),
            ])
            
            return True
        except Exception as e:
            self.logger.warning(f"Failed to setup AI analysis: {e}")
            return False

    def _setup_search(self) -> bool:
        """Set up web search capabilities using LangChain DuckDuckGo search."""
        try:
            # Initialize DuckDuckGo search wrapper
            self.search_wrapper = DuckDuckGoSearchAPIWrapper(
                max_results=5,
                region="us-en",
                safesearch="moderate"
            )
            self.search_tool = DuckDuckGoSearchRun(api_wrapper=self.search_wrapper)
            self.logger.info("🔍 Web search capabilities enabled (DuckDuckGo)")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to setup web search: {e}")
            return False

    def search_for_replacement(self, broken_url: str) -> Optional[ValidatedReplacement]:
        """Search for a working replacement URL using LangChain web search."""
        try:
            # Extract key terms from the broken URL for search
            search_terms = self._extract_search_terms(broken_url)
            self.logger.info(f"🔍 Searching for: {search_terms}")

            # Perform web search using LangChain DuckDuckGo
            search_results = self._perform_web_search(search_terms)

            if not search_results:
                return None

            # Parse search results and extract URLs
            candidate_urls = self._parse_search_results(search_results)

            # Validate and test the candidate URLs
            for candidate_url, description in candidate_urls[:5]:  # Check top 5 results
                if self._is_valid_replacement(broken_url, candidate_url):
                    self.logger.info(f"🧪 Testing candidate: {candidate_url}")
                    # Test if the candidate URL actually works
                    test_result = self.check_url(candidate_url)
                    if test_result.status == 'PASS':
                        return ValidatedReplacement(
                            original_url=broken_url,
                            replacement_url=candidate_url,
                            confidence='HIGH',
                            validation_method='web_search_and_test',
                            description=description
                        )
                    else:
                        self.logger.info(f"❌ Candidate failed: {candidate_url} - {test_result.error_message}")

            return None

        except Exception as e:
            self.logger.warning(f"Search for replacement failed: {e}")
            return None

    def _extract_search_terms(self, url: str) -> str:
        """Extract meaningful search terms from a broken URL."""
        # Extract key components from OpenShift documentation URLs
        if 'openshift_container_platform' in url:
            parts = url.split('/')

            # Extract version, topic, and specific page
            version = None
            topic = None
            page = None

            for i, part in enumerate(parts):
                if part.startswith('4.'):
                    version = part
                elif part in ['html', 'html-single'] and i + 1 < len(parts):
                    topic = parts[i + 1]
                elif part.endswith('.html') or (topic and i > parts.index(topic)):
                    page = part.replace('.html', '').replace('-', ' ')
                    break

            # Build search query
            search_terms = "OpenShift Container Platform"
            if topic:
                search_terms += f" {topic.replace('-', ' ')}"
            if page:
                search_terms += f" {page}"
            search_terms += " site:docs.redhat.com"

            return search_terms

        # Fallback for other URLs
        return f"OpenShift documentation {url.split('/')[-1].replace('-', ' ')} site:docs.redhat.com"

    def _perform_web_search(self, query: str) -> str:
        """Perform web search using LangChain DuckDuckGo search."""
        try:
            # Use the LangChain search tool
            search_results = self.search_tool.run(query)
            return search_results
        except Exception as e:
            self.logger.warning(f"Web search failed: {e}")
            return ""

    def _parse_search_results(self, search_results: str) -> List[tuple]:
        """Parse search results and extract URLs with descriptions."""
        candidates = []

        if not search_results:
            return candidates

        # Split search results into lines and look for URLs
        lines = search_results.split('\n')
        current_title = ""

        for line in lines:
            line = line.strip()

            # Look for URLs in the search results
            if 'docs.redhat.com' in line and 'openshift' in line.lower():
                # Extract URL from the line
                import re
                url_match = re.search(r'https://docs\.redhat\.com[^\s\]]+', line)
                if url_match:
                    url = url_match.group(0)
                    # Clean up URL (remove trailing punctuation)
                    url = re.sub(r'[.,;)\]]+$', '', url)

                    # Use the line as description or previous title
                    description = current_title if current_title else line
                    candidates.append((url, description))

            # Keep track of potential titles
            elif line and not line.startswith('http') and len(line) > 10:
                current_title = line[:100]  # Limit title length

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for url, desc in candidates:
            if url not in seen:
                seen.add(url)
                unique_candidates.append((url, desc))

        return unique_candidates



    def _is_valid_replacement(self, original_url: str, candidate_url: str) -> bool:
        """Check if a candidate URL is a valid replacement for the original."""
        # Must be from the same domain
        if not candidate_url.startswith('https://docs.redhat.com'):
            return False

        # Must be OpenShift documentation
        if 'openshift_container_platform' not in candidate_url:
            return False

        # Extract topic from original URL
        original_parts = original_url.split('/')
        candidate_parts = candidate_url.split('/')

        # Look for similar topics
        original_topic = None
        candidate_topic = None

        for part in original_parts:
            if part in ['observability', 'monitoring', 'storage', 'networking', 'backup_and_restore']:
                original_topic = part
                break

        for part in candidate_parts:
            if part in ['observability', 'monitoring', 'storage', 'networking', 'backup_and_restore']:
                candidate_topic = part
                break

        # Topics should match or be related
        if original_topic and candidate_topic:
            # Allow observability <-> monitoring as they're related
            related_topics = {
                'observability': ['monitoring'],
                'monitoring': ['observability']
            }

            if original_topic == candidate_topic:
                return True
            elif original_topic in related_topics and candidate_topic in related_topics[original_topic]:
                return True

        return False
    
    def analyze_failures(self, results: List[ModuleResult]) -> Optional[IntelligentAnalysis]:
        """Use AI to analyze link failures and provide recommendations."""
        if not self.ai_enabled:
            return None
            
        # Collect all failed links
        failed_links = []
        for result in results:
            for link in result.links:
                if link.status == 'FAIL':
                    failed_links.append({
                        'url': link.url,
                        'module': result.module_name,
                        'error': link.error_message,
                        'status_code': link.status_code
                    })
        
        if not failed_links:
            return None

        # Search for validated replacements for each broken link
        validated_replacements = []
        if self.search_enabled:
            self.logger.info("🔍 Searching for validated replacement URLs...")
            for link_info in failed_links:
                replacement = self.search_for_replacement(link_info['url'])
                if replacement:
                    validated_replacements.append(replacement)
                    self.logger.info(f"✅ Found replacement: {replacement.replacement_url}")
                else:
                    self.logger.info(f"❌ No replacement found for: {link_info['url']}")

        # Prepare analysis input
        analysis_input = {
            "workshop_context": "OpenShift 4.18/4.19 Bare Metal Deployment Workshop",
            "failed_links": failed_links,
            "total_modules": len(results),
            "total_failed": len(failed_links)
        }
        
        # Include validated replacements in the analysis
        replacements_text = ""
        if validated_replacements:
            replacements_text = f"""

        Validated Replacement URLs Found:
        {json.dumps([asdict(r) for r in validated_replacements], indent=2)}
        """

        prompt_text = f"""
        Analyze the following broken documentation links from the OpenShift Bare Metal Workshop:

        Workshop Context: {analysis_input['workshop_context']}
        Total Modules Affected: {analysis_input['total_modules']}
        Total Failed Links: {analysis_input['total_failed']}

        Failed Links:
        {json.dumps(failed_links, indent=2)}
        {replacements_text}

        Please provide:
        1. Pattern Analysis: What patterns do you see in the broken links?
        2. Impact Assessment: How do these broken links affect workshop participants?
        3. Specific Recommendations: What should be done to fix each category of broken links?
        4. Validated Replacements: For each broken link, recommend the validated replacement URL if found, or suggest search strategies if not found.

        Format your response as structured analysis with clear sections.
        Focus on the validated replacement URLs that have been tested and confirmed to work.
        """
        
        try:
            prompt = self.analysis_template.invoke({"input": prompt_text})
            response = self.llm.invoke(input=prompt)
            
            # Parse AI response and create structured analysis
            analysis_text = response.content
            
            # Extract recommendations (simple parsing)
            recommendations = self._extract_recommendations(analysis_text)
            
            # Generate GitHub issue content
            github_title = f"🔗 Broken Documentation Links Detected - {len(failed_links)} failures"
            github_body = self._generate_github_issue_body(failed_links, analysis_text, validated_replacements)
            
            return IntelligentAnalysis(
                broken_links=[link['url'] for link in failed_links],
                analysis=analysis_text,
                recommendations=recommendations,
                impact_assessment=self._extract_impact_assessment(analysis_text),
                github_issue_title=github_title,
                github_issue_body=github_body,
                validated_replacements=validated_replacements
            )
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract actionable recommendations from AI analysis."""
        recommendations = []
        lines = analysis_text.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if 'recommendation' in line.lower() or 'fix' in line.lower():
                in_recommendations = True
                continue
            if in_recommendations and line.startswith(('- ', '* ', '1. ', '2. ', '3. ')):
                recommendations.append(line.lstrip('- *123456789. '))
            elif in_recommendations and line == '':
                continue
            elif in_recommendations and not line.startswith(('- ', '* ', '1. ', '2. ', '3. ')):
                break
                
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _extract_impact_assessment(self, analysis_text: str) -> str:
        """Extract impact assessment from AI analysis."""
        lines = analysis_text.split('\n')
        impact_lines = []
        
        in_impact = False
        for line in lines:
            if 'impact' in line.lower():
                in_impact = True
                continue
            if in_impact:
                if line.strip() and not line.startswith('#'):
                    impact_lines.append(line.strip())
                elif len(impact_lines) > 0 and line.strip() == '':
                    break
                    
        return ' '.join(impact_lines[:3])  # First 3 sentences
    
    def _generate_github_issue_body(self, failed_links: List[Dict], analysis: str,
                                   validated_replacements: List[ValidatedReplacement] = None) -> str:
        """Generate GitHub issue body with AI analysis and validated replacements."""
        body = f"""# 🔗 Broken Documentation Links Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Workshop:** OpenShift 4.18/4.19 Bare Metal Deployment
**Failed Links:** {len(failed_links)}
**Validated Replacements Found:** {len(validated_replacements) if validated_replacements else 0}

## 🤖 AI Analysis

{analysis}

## ✅ Validated Replacement URLs

"""

        # Add validated replacements section
        if validated_replacements:
            for replacement in validated_replacements:
                body += f"""### {replacement.original_url}
**✅ Replacement Found:** `{replacement.replacement_url}`
- **Confidence:** {replacement.confidence}
- **Validation:** {replacement.validation_method}
- **Description:** {replacement.description}

"""
        else:
            body += "No validated replacements found through automated search.\n\n"

        body += "## 📋 Broken Links Details\n\n"
        
        # Group by module
        modules = {}
        for link in failed_links:
            module = link['module']
            if module not in modules:
                modules[module] = []
            modules[module].append(link)
        
        for module, links in modules.items():
            body += f"### {module}\n\n"
            for link in links:
                body += f"- ❌ `{link['url']}`\n"
                body += f"  - **Error**: {link['error']}\n"
                if link['status_code']:
                    body += f"  - **Status Code**: {link['status_code']}\n"
                body += "\n"
        
        body += """
## 🔧 Next Steps

1. Review the AI analysis above for patterns and recommendations
2. Update broken links according to the suggested fixes
3. Run the link checker again to verify fixes: `python3 scripts/intelligent_link_checker.py`
4. Close this issue once all links are working

## 🤖 Automation

This issue was created automatically by the Intelligent Link Checker with AI analysis.

---
*Generated by OpenShift Workshop Intelligent Link Checker*
"""
        
        return body
    
    def create_github_issue(self, analysis: IntelligentAnalysis, github_token: Optional[str] = None, 
                          repo: str = "openshift-bare-metal-deployment-workshop") -> bool:
        """Create a GitHub issue for broken links."""
        if not github_token:
            github_token = os.getenv('GITHUB_TOKEN')
            
        if not github_token:
            self.logger.warning("No GitHub token provided. Cannot create issue.")
            return False
        
        # Extract owner/repo from repo string
        if '/' in repo:
            owner, repo_name = repo.split('/', 1)
        else:
            owner = "your-username"  # Default - should be configured
            repo_name = repo
        
        url = f"https://api.github.com/repos/{owner}/{repo_name}/issues"
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': analysis.github_issue_title,
            'body': analysis.github_issue_body,
            'labels': ['documentation', 'bug', 'automated', 'link-checker']
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                issue_data = response.json()
                self.logger.info(f"✅ GitHub issue created: {issue_data['html_url']}")
                return True
            else:
                self.logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error creating GitHub issue: {e}")
            return False
    
    def generate_intelligent_report(self, results: List[ModuleResult], analysis: Optional[IntelligentAnalysis] = None) -> None:
        """Generate enhanced report with AI analysis."""
        # Generate base report
        super().generate_report(results)
        
        if not analysis:
            return
            
        # Append AI analysis to report
        report_file = self.config['output']['issue_file']
        
        with open(report_file, 'a') as f:
            f.write("\n## 🤖 AI Analysis\n\n")
            f.write(analysis.analysis)

            # Add validated replacements section
            if analysis.validated_replacements:
                f.write("\n\n## ✅ Validated Replacement URLs\n\n")
                for replacement in analysis.validated_replacements:
                    f.write(f"### {replacement.original_url}\n")
                    f.write(f"**✅ Replacement:** `{replacement.replacement_url}`\n")
                    f.write(f"- **Confidence:** {replacement.confidence}\n")
                    f.write(f"- **Validation:** {replacement.validation_method}\n")
                    f.write(f"- **Description:** {replacement.description}\n\n")

            f.write("\n## 🎯 Recommendations\n\n")
            for i, rec in enumerate(analysis.recommendations, 1):
                f.write(f"{i}. {rec}\n")

            f.write(f"\n## 📊 Impact Assessment\n\n")
            f.write(analysis.impact_assessment)

            f.write("\n\n---\n")
            f.write("*Enhanced with AI analysis and validated URL search using Granite 3.3 8B Instruct model*\n")
        
        self.logger.info("🤖 Enhanced report with AI analysis generated")

def main():
    """Main function for intelligent link checker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intelligent OpenShift Workshop Link Checker')
    parser.add_argument('files', nargs='*', help='Files to check (default: all modules)')
    parser.add_argument('--config', default='scripts/link-checker-config.json', 
                       help='Configuration file path')
    parser.add_argument('--test-mode', action='store_true', 
                       help='Test mode: check only first 3 links per file')
    parser.add_argument('--max-links', type=int, 
                       help='Maximum number of links to check per file')
    parser.add_argument('--create-github-issue', action='store_true',
                       help='Create GitHub issue for broken links')
    parser.add_argument('--github-repo', default='openshift-bare-metal-deployment-workshop',
                       help='GitHub repository (format: owner/repo)')
    
    args = parser.parse_args()
    
    # Initialize intelligent checker
    checker = IntelligentLinkChecker(args.config)
    
    if not checker.ai_enabled:
        checker.logger.warning("AI analysis not available. Falling back to basic link checking.")
    
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
    
    if not results:
        checker.logger.error("No files processed")
        sys.exit(1)
    
    # Perform AI analysis if enabled
    analysis = None
    if checker.ai_enabled:
        checker.logger.info("🤖 Performing AI analysis of link failures...")
        analysis = checker.analyze_failures(results)
        if analysis:
            checker.logger.info("✅ AI analysis completed")
        else:
            checker.logger.info("ℹ️ No failures to analyze")
    
    # Generate enhanced report
    checker.generate_intelligent_report(results, analysis)
    
    # Create GitHub issue if requested and there are failures
    if args.create_github_issue and analysis:
        checker.logger.info("🐙 Creating GitHub issue...")
        success = checker.create_github_issue(analysis, repo=args.github_repo)
        if not success:
            checker.logger.warning("Failed to create GitHub issue. Check token and repository settings.")
    
    # Exit with appropriate code
    total_failed = sum(r.failed_links for r in results)
    if total_failed > 0:
        checker.logger.error(f"❌ Link validation completed with {total_failed} failures")
        if analysis:
            checker.logger.info("🤖 AI analysis available in report")
        sys.exit(1)
    else:
        checker.logger.info("🎉 All links are working correctly!")
        sys.exit(0)

if __name__ == "__main__":
    main()
