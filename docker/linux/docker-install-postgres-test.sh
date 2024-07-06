docker exec -i test-postgres bash -c "
until pg_isready -h test-postgres -p 5432 -U postgres
do
  echo \"Waiting for PostgreSQL...\"
  sleep 1
done
psql -U root -d postgres -c 'CREATE DATABASE \"test-enterpriseEMS\";'
psql -U root -d test-enterpriseEMS -f /tmp/sql/ems_ai.sql
psql -U root -d test-enterpriseEMS -f /tmp/sql/system-data.sql
psql -U root -d test-enterpriseEMS -f /tmp/sql/testing-data.sql
"