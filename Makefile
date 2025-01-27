# Define the directory containing the utilities
UTILITIES_DIR = utilities

# Define the commands
LAB_SERVE = $(UTILITIES_DIR)/lab-serve
LAB_STOP = $(UTILITIES_DIR)/lab-stop
LAB_BUILD = $(UTILITIES_DIR)/lab-build
LAB_CLEAN = $(UTILITIES_DIR)/lab-clean

# Default target
all: help

# Target to display help
help:
	@echo "Available targets:"
	@echo "  help        - Display this help message"
	@echo "  serve       - Run lab-serve"
	@echo "  stop        - Run lab-stop"
	@echo "  build       - Run lab-build"
	@echo "  clean       - Run lab-clean"
	@echo "  run-all     - Run build and then serve"
	@echo "  stop-clean  - Run stop and then clean"
	@echo "  clean-build - Run clean and then build"

# Target to run lab-serve
serve:
	@echo "Running lab-serve..."
	@$(LAB_SERVE)

# Target to run lab-stop
stop:
	@echo "Running lab-stop..."
	@$(LAB_STOP)

# Target to run lab-build
build:
	@echo "Running lab-build..."
	@$(LAB_BUILD)

# Target to run lab-clean
clean:
	@echo "Running lab-clean..."
	@$(LAB_CLEAN)

# Target to run all commands in sequence
run-all: build serve

# Target to stop and clean
stop-clean: stop clean

# Target to clean and build
clean-build: clean build

# Phony targets
.PHONY: all help serve stop build clean run-all stop-clean clean-build
