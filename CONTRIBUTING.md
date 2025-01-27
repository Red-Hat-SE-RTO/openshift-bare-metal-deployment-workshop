# Contributing to OpenShift 4.16+ Bare Metal Deployment Workshop

Thank you for your interest in contributing to the OpenShift 4.16+ Bare Metal Deployment Workshop! This document provides guidelines and instructions for contributing to this repository.

## Table of Contents

1. [Fork and Clone the Repository](#fork-and-clone-the-repository)
2. [Repository Structure](#repository-structure)
3. [Making Changes](#making-changes)
4. [Content Guidelines](#content-guidelines)
5. [Using Utility Scripts](#using-utility-scripts)
6. [GitHub Actions](#github-actions)
7. [Building and Testing Locally](#building-and-testing-locally)
8. [Submitting Changes](#submitting-changes)
9. [Using This Repository for Your Environment](#using-this-repository-for-your-environment)

## Fork and Clone the Repository

1. Fork this repository by clicking the "Fork" button in the top-right corner of this repository's page.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/openshift-bare-metal-deployment-workshop.git
   cd openshift-bare-metal-deployment-workshop
   ```
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/Red-Hat-SE-RTO/openshift-bare-metal-deployment-workshop.git
   ```

## Repository Structure

```
.
├── content/
│   └── modules/
│       └── ROOT/
│           ├── assets/
│           │   └── images/
│           │       ├── module-01/
│           │       ├── module-02/
│           │       └── ...
│           ├── pages/
│           │   ├── module-01-introduction.adoc
│           │   ├── module-02-infrastructure.adoc
│           │   └── ...
│           └── nav.adoc
├── utilities/
│   ├── lab-build
│   ├── lab-clean
│   ├── lab-serve
│   └── lab-stop
├── .github/
│   └── workflows/
│       └── deploy-pages.yml
├── Makefile
├── default-site.yml
├── demo-site.yml
└── README.adoc
```

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our content guidelines.

3. Commit your changes with descriptive commit messages:
   ```bash
   git add .
   git commit -m "feat: add detailed networking configuration examples"
   ```

## Content Guidelines

### Document Structure
- Use AsciiDoc format for documentation (`.adoc` extension)
- Follow the existing module structure
- Include clear section headers with anchors
- Use consistent formatting

### Images
- Place images in the appropriate module folder under `content/modules/ROOT/assets/images/`
- Use meaningful file names
- Optimize images for web viewing
- Include alt text for accessibility

### Code Examples
- Include clear, well-documented code examples
- Use code blocks with appropriate language tags
- Test all code examples before submitting

## Using Utility Scripts

The repository includes several utility scripts in the `utilities/` directory and a Makefile to help you build and test the documentation locally.

### Available Make Targets

```bash
make help        # Display help message
make serve       # Start the local server
make stop        # Stop the local server
make build       # Build the documentation
make clean       # Clean the build directory
make run-all     # Build and serve the documentation
make stop-clean  # Stop server and clean build directory
make clean-build # Clean and rebuild the documentation
```

### Utility Scripts

1. **lab-build**
   - Builds the documentation site using Antora
   - Creates output in the `./www` directory
   ```bash
   ./utilities/lab-build
   ```

2. **lab-serve**
   - Starts a local HTTP server using podman/docker
   - Serves content on http://localhost:8080
   ```bash
   ./utilities/lab-serve
   ```

3. **lab-stop**
   - Stops the local HTTP server
   ```bash
   ./utilities/lab-stop
   ```

4. **lab-clean**
   - Removes the generated site content
   ```bash
   ./utilities/lab-clean
   ```

### Common Workflows

1. **First-time setup**:
   ```bash
   make clean-build  # Clean and build the site
   make serve        # Start the local server
   ```

2. **Development cycle**:
   ```bash
   make run-all     # Build and serve in one command
   # Make your changes
   make build       # Rebuild after changes
   ```

3. **Cleaning up**:
   ```bash
   make stop-clean  # Stop server and clean build directory
   ```

## GitHub Actions

This repository uses GitHub Actions for automated deployment to GitHub Pages. The workflow (`deploy-pages.yml`) does the following:

1. Triggers on:
   - Pushes to the main branch
   - Manual workflow dispatch

2. Deployment Process:
   - Checks out the repository
   - Sets up the build environment
   - Builds the documentation using Antora
   - Deploys to GitHub Pages

To use GitHub Actions in your fork:

1. Enable GitHub Pages in your repository settings
2. Configure the necessary permissions
3. The workflow will automatically deploy changes pushed to your main branch


## Submitting Changes

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template
   - Submit the PR

## Using This Repository for Your Environment

To customize this workshop for your environment:

1. Fork the repository as described above.

2. Update configuration files:
   - Edit `default-site.yml` and `demo-site.yml` with your site information
   - Modify `content/antora.yml` with your version information

3. Customize content:
   - Update module content in `content/modules/ROOT/pages/`
   - Add your own images to `content/modules/ROOT/assets/images/`
   - Modify navigation in `content/modules/ROOT/nav.adoc`

4. Environment-specific changes:
   - Update hardware requirements
   - Modify network configurations
   - Adjust storage settings
   - Add specific use cases

5. Deploy:
   - Push changes to your repository
   - GitHub Actions will automatically build and deploy to your GitHub Pages

6. Maintain:
   - Regularly update content
   - Keep OpenShift version information current
   - Address user feedback and issues

Remember to:
- Keep your fork updated with upstream changes
- Document any environment-specific modifications
- Test all changes thoroughly before deployment
- Maintain security best practices

## Questions or Need Help?

If you have questions or need help with contributing:
1. Check existing issues
2. Create a new issue
3. Reach out to the maintainers

Thank you for contributing to making this workshop better for everyone!
