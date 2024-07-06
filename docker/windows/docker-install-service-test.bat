@echo off
cd ..

:: 等待 PostgreSQL 准备就绪
:WAITFORPOSTGRE
docker exec -it test-postgres psql -U root -d postgres -c "SELECT 1;" 2>nul
IF %errorlevel% NEQ 0 (
    echo Waiting for PostgreSQL to become ready...
    timeout /t 1 /nobreak > nul
    goto WAITFORPOSTGRE
)

:: 在容器中执行多个 PostgreSQL 命令
docker exec -it test-postgres psql -U root -d postgres -c "CREATE DATABASE \"test-enterpriseEMS\";"
docker exec -it test-postgres psql -U root -d test-enterpriseEMS -f /tmp/sql/ems_ai.sql
docker exec -it test-postgres psql -U root -d test-enterpriseEMS -f /tmp/sql/system-data.sql
docker exec -it test-postgres psql -U root -d test-enterpriseEMS -f /tmp/sql/testing-data.sql