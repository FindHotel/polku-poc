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
dev: .env
	$(PIP) install -r requirements-test.txt

# remove .env
clean:
	rm -rf .env .lambda

# configure humilis
configure:
	$(HUMILIS) configure --local

# deploy
create: install
	$(HUMILIS) create \
		--stage $(STAGE) \
		--output $(HUMILIS_ENV)-$(STAGE).outputs.yaml \
		--parameters $(PARAMETERS) \
		$(HUMILIS_ENV).yaml.j2

# update an existing deployment
update: install
	$(HUMILIS) update \
		--stage $(STAGE) \
		--output $(HUMILIS_ENV)-$(STAGE).outputs.yaml \
		--parameters $(PARAMETERS) \
		$(HUMILIS_ENV).yaml.j2

# destroy a deployment
delete: install
	$(HUMILIS) delete \
		--stage $(STAGE) \
		--parameters $(PARAMETERS) \
		$(HUMILIS_ENV).yaml.j2

# run unit tests
test: .env
	$(PIP) install tox
	$(TOX) -e unit

# run integration tests: will create a test deployment
testi: .env
	$(PIP) install tox
	$(TOX) -e integration
