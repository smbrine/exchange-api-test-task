.PHONY: run black docker check

run:
	poetry run python -m app.main

black:
	poetry run black -l 75 .

docker:
	export CI_TAG=v1.1.1; \
	export REGISTRY=docker.io/smbrine; \
	export REPO=exchange-api-test-task; \
	export FULL_REPO=$$REGISTRY/$$REPO; \
	export CI_TAG_MAJOR=$$(echo $$CI_TAG | cut -d'.' -f1); \
	export CI_TAG_MINOR=$$(echo $$CI_TAG | cut -d'.' -f1-2); \
	export BUILDPLATFORM=linux/amd64; \
	docker build --platform=linux/amd64 --build-arg BUILDPLATFORM=linux/amd64 --build-arg DOCKER_TAG=$$CI_TAG --build-arg IMAGE=$$FULL_REPO -t $$FULL_REPO:$$CI_TAG .; \
	docker tag $$FULL_REPO:$$CI_TAG $$FULL_REPO:$$CI_TAG_MINOR; \
	docker tag $$FULL_REPO:$$CI_TAG $$FULL_REPO:$$CI_TAG_MAJOR; \
	docker tag $$FULL_REPO:$$CI_TAG $$FULL_REPO:latest; \
	docker push $$FULL_REPO:$$CI_TAG_MAJOR; \
	docker push $$FULL_REPO:latest; \
	docker push $$FULL_REPO:$$CI_TAG_MINOR; \
	docker push $$FULL_REPO:$$CI_TAG


check: black
	poetry run flake8 .
	poetry run ruff check .
	poetry run pylint .
	poetry run mypy .