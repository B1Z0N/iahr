docker-compose \
  -f docker-compose.yml \
  -f docker-compose.deploy.yml \
  pull

docker-compose \
  -f docker-compose.deploy.yml \
  up -d
