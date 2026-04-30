COMPOSE ?= docker-compose
SERVICE ?= risk-game
CONTAINER_NAME ?= risk-game-container
IN_CONTAINER := $(shell [ -f /.dockerenv ] && echo 1 || echo 0)

USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
USER_NAME := $(shell whoami)
GAME_RESULTS_HOST_PATH ?= $(HOME)/shared/risk-game/game_results

export USER_ID
export GROUP_ID
export USER_NAME
export GAME_RESULTS_HOST_PATH

ARGS ?=

.PHONY: up shell test test-regression test-live test-live-canary test-live-canary-openai test-live-canary-gemini test-live-canary-moonshot run-example run-experiment experiment-status experiment-summary experiment-series-summary logs down

ifeq ($(IN_CONTAINER),1)
RUN_IN_SERVICE :=
else
RUN_IN_SERVICE := $(COMPOSE) exec -T $(SERVICE)
endif

up:
ifeq ($(IN_CONTAINER),1)
	@echo "Already inside the container. Run 'make up' from the host."
	@exit 1
else
	mkdir -p "$(GAME_RESULTS_HOST_PATH)"
	$(COMPOSE) up --build -d
endif

shell:
ifeq ($(IN_CONTAINER),1)
	bash
else
	docker exec -it $(CONTAINER_NAME) bash
endif

test:
	$(RUN_IN_SERVICE) pytest tests/

test-regression:
	$(RUN_IN_SERVICE) pytest tests/

test-live:
	$(RUN_IN_SERVICE) pytest -m live_api tests/

test-live-canary:
	$(RUN_IN_SERVICE) pytest -m credit_canary tests/

test-live-canary-openai:
	$(RUN_IN_SERVICE) pytest tests/test_openai_credit_canary.py

test-live-canary-gemini:
	$(RUN_IN_SERVICE) pytest tests/test_gemini_credit_canary.py

test-live-canary-moonshot:
	$(RUN_IN_SERVICE) pytest tests/test_moonshot_credit_canary.py

run-example:
	$(RUN_IN_SERVICE) python scripts/example_run.py

run-experiment:
	$(RUN_IN_SERVICE) python scripts/run_experiment.py $(ARGS)

experiment-status:
	$(RUN_IN_SERVICE) python scripts/experiment_status.py $(ARGS)

experiment-summary:
	$(RUN_IN_SERVICE) python scripts/experiment_summary.py $(ARGS)

experiment-series-summary:
	$(RUN_IN_SERVICE) python scripts/experiment_series_summary.py $(ARGS)

logs:
ifeq ($(IN_CONTAINER),1)
	@echo "Container logs are a host-side operation. Run 'make logs' from the host."
	@exit 1
else
	$(COMPOSE) logs -f $(SERVICE)
endif

down:
ifeq ($(IN_CONTAINER),1)
	@echo "Stopping the stack is a host-side operation. Run 'make down' from the host."
	@exit 1
else
	$(COMPOSE) down
endif
