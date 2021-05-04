set COMPOSE_CONVERT_WINDOWS_PATHS=1
docker-compose -p app_proxy up -d --build
pause
docker-compose -p app_proxy down
