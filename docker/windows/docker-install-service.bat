@echo off
cd ..\..
mkdir %cd%\models
mkdir %cd%\meta_data
mkdir \data\database \data\database\postgresql \data\ems-enterprise-ai \data\ems-enterprise-ai\logs 

:: 授予写入权限
icacls \data\ems-enterprise-ai\ /grant Everyone:(OI)(CI)F
icacls \data\database\ /grant Everyone:(OI)(CI)F
icacls %cd%\models\ /grant Everyone:(OI)(CI)F
icacls %cd%\meta_data\ /grant Everyone:(OI)(CI)F

cd docker
:: 启动 Docker Compose
docker-compose -f docker-compose.postgre.install.yml up -d
:: 等待 PostgreSQL 准备就绪
:WAITFORPOSTGRE
docker exec -it postgre-install psql -U root -d postgres -c "SELECT 1;" 2>nul
IF %errorlevel% NEQ 0 (
    echo Waiting for PostgreSQL to become ready...
    timeout /t 1 /nobreak > nul
    goto WAITFORPOSTGRE
)

:: 在容器中执行多个 PostgreSQL 命令
docker exec -it postgre-install psql -U root -d postgres -c "CREATE DATABASE \"enterpriseEMS\";"
docker exec -it postgre-install psql -U root -d enterpriseEMS -f /tmp/sql/ems_ai.sql
docker exec -it postgre-install psql -U root -d enterpriseEMS -f /tmp/sql/system-data.sql


:: 输出完成消息
echo Install PostgreSQL finished.

:: 删除 postgre-install 容器
docker rm -f postgre-install

:: 输出移除容器消息
echo Remove postgre-install container.

cd windows