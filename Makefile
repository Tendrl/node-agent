NAME=tendrl-node-agent
VERSION := $(shell PYTHONPATH=. python -c \
             'import tendrl.node_agent; print tendrl.node_agent.__version__')
RELEASE=1

all: srpm

clean:
	rm -rf dist/
	rm -rf $(NAME)-$(VERSION).tar.gz
	rm -rf $(NAME)-$(VERSION)-1.el7.src.rpm

dist:
	python setup.py sdist \
	  && mv dist/$(NAME)-$(VERSION).tar.gz .

srpm: dist
	fedpkg --dist epel7 srpm

rpm: dist
	mock -r epel-7-x86_64 rebuild $(NAME)-$(VERSION)-$(RELEASE).el7.src.rpm --resultdir=. --define "dist .el7"

.PHONY: dist rpm srpm
