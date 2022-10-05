# Project utility scripts
.PHONY: test

# Setup environment
export SRC_DIR := ./src/python
export TEST_DIR := ./test/python
export PYTHONPATH := ${SRC_DIR}:${TEST_DIR}:${PYTHONPATH}
export PATH := ${TEST_DIR}:${PATH}
export PYTHONWARNINGS := ignore
export TOKENIZERS_PARALLELISM := False

# Default python executable if not provided
PYTHON ?= python

# Download test data
data: 
	mkdir -p /tmp/codequestion
	wget -N https://archive.org/download/stackexchange_20220606/ai.stackexchange.com.7z -P /tmp/codequestion/stackexchange/ai
	wget -N https://raw.githubusercontent.com/neuml/codequestion/master/config/index.v1.yml -P /tmp/codequestion/
	wget -N https://raw.githubusercontent.com/neuml/codequestion/master/config/index.yml -P /tmp/codequestion/

	wget https://raw.githubusercontent.com/neuml/codequestion/master/test/stackexchange/query.txt -P /tmp/codequestion/test/stackexchange
	wget http://ixa2.si.ehu.es/stswiki/images/4/48/Stsbenchmark.tar.gz -P /tmp/codequestion
	tar -C /tmp/codequestion/test -xvzf /tmp/codequestion/Stsbenchmark.tar.gz

# Unit tests
test:
	${PYTHON} -m unittest discover -v -s ${TEST_DIR}

# Run tests while calculating code coverage
coverage:
	coverage run -m unittest discover -v -s ${TEST_DIR}
	coverage combine
