# store the current working directory
CWD := $(shell pwd)
BASEDIR := $(CWD)
PRINT_STATUS = export EC=$$?; cd $(CWD); if [ "$$EC" -eq "0" ]; then printf "SUCCESS!\n"; else exit $$EC; fi
VERSION=0.0.1

BUILDS    := .build
DEPLOY    := $(BUILDS)/deploy
PKGNAME   := tendrl-node-agent
TARDIR    := ${PKGNAME}-$(VERSION)
RPMBUILD  := $(HOME)/rpmbuild


dist:
	rm -fr $(HOME)/$(BUILDS)
	mkdir -p $(HOME)/$(BUILDS) $(RPMBUILD)/SOURCES
	cp -fr $(BASEDIR) $(HOME)/$(BUILDS)/$(TARDIR)
	rm -rf %{pkg_name}.egg-info
	cd $(HOME)/$(BUILDS); \
	tar --exclude-vcs --exclude=.* -zcf tendrl-node-agent-$(VERSION).tar.gz $(TARDIR); \
	cp tendrl-node-agent-$(VERSION).tar.gz $(RPMBUILD)/SOURCES
        # Cleaning the work directory
	rm -fr $(HOME)/$(BUILDS)


rpm:
	@echo "target: rpm"
	@echo  "  ...building rpm $(V_ARCH)..."
	rm -fr $(BUILDS)
	mkdir -p $(DEPLOY)/latest
	mkdir -p $(RPMBUILD)/SPECS
	sed -e "s/@VERSION@/$(VERSION)/" node_agent.spec \
	        > $(RPMBUILD)/SPECS/node_agent.spec
	rpmbuild -ba $(RPMBUILD)/SPECS/node_agent.spec
	$(PRINT_STATUS); \
	if [ "$$EC" -eq "0" ]; then \
		FILE=$$(readlink -f $$(find $(RPMBUILD)/RPMS -name tendrl-node-agent-$(VERSION)*.rpm)); \
		cp -f $$FILE $(DEPLOY)/latest/; \
		printf "\nThe bridge common RPMs are located at:\n\n"; \
		printf "   $(DEPLOY)/latest\n\n\n\n"; \
	fi
