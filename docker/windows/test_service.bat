cd ..
REM 设置环境变量
SET PROJECT_DIR=/home/app/workdir
set DOCKER_NETWORK_NAME=test-enterprise-ems

:: 创建 Docker 网络
docker network create %DOCKER_NETWORK_NAME%

:: 启动 PostgreSQL 容器
docker run -d --network %DOCKER_NETWORK_NAME% --name test-postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -e POSTGRES_DB=test-enterpriseEMS -p 5432 -v %CD%\..\data\sql\postgresql:/tmp/sql postgres:13.5-alpine

docker run -itd --network %DOCKER_NETWORK_NAME% --expose=6379 --name test-redis redis:6.0-alpine

call ./windows/docker-install-service-test.bat

docker run -itd --user root --network %DOCKER_NETWORK_NAME% --env-file %CD%\docker\unittest.env -v  %CD%:%PROJECT_DIR% -w %PROJECT_DIR% -e PYTHONPATH=%PROJECT_DIR% --name test-celery-worker python:3.10-slim-bookworm /bin/bash  -c "apt-get update && pip install --upgrade pip && pip3 install -r docker/requirements.txt && pip3 install -r docker/requirements-test.txt && celery -A src.service.event.celery_app worker --loglevel=INFO --concurrency=4"

docker run --rm --user root --network %DOCKER_NETWORK_NAME% --env-file %CD%\docker\unittest.env -v  %CD%:%PROJECT_DIR% -w %PROJECT_DIR% -e PYTHONPATH=%PROJECT_DIR% python:3.10-slim-bookworm /bin/bash  -c "apt-get update && pip install --upgrade pip && pip3 install -r docker/requirements.txt && pip3 install -r docker/requirements-test.txt && pytest -q -p no:warnings --cov-config=config/.pytest_coveragerc --cov=. --cov-report term-missing -o log_cli=true --capture=no tests/"

docker rm -f test-postgres
docker rm -f test-redis
docker rm -f test-celery-worker
docker network rm %DOCKER_NETWORK_NAME%

cd docker/windows

