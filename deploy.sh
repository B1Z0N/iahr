docker-compose \
  -f docker-compose.yml \
  -f docker-compose.pull.yml \
  pull

docker-compose \
  -f docker-compose.yml \
  -f docker-compose.pull.yml \
  up -d
