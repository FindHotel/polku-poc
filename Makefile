HUMILIS := .env/bin/humilis
PIP := .env/bin/pip
TOX := .env/bin/tox
PYTHON := .env/bin/python
STAGE := DEV
HUMILIS_ENV := polkupoc
PARAMETERS := parameters.yaml


# create virtual environment
.env:
	virtualenv .env -p python3

# install deployment dependencies
install: .env
	$(PIP) install -e .

# install dev dependencies
develop: .env
	$(PIP) install -r requirements-test.txt

# remove .env
clean:
	rm -rf .env .lambda

# configure humilis
configure:
	$(HUMILIS) configure --local

# run unit tests
test: .env
	$(PIP) install tox
	$(TOX) -e unit

# run integration tests: will create a test deployment
testi: .env
	$(PIP) install tox
	$(TOX) -e integration
