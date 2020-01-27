docker-compose \
  -f docker-compose.yml \
  -f docker-compose.deploy.yml \
  build

docker-compose \
  -f docker-compose.yml \
  -f docker-compose.deploy.yml \
  push
