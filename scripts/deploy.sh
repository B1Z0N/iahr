export DOCKER_HOST="ssh://kraftwerk28.pp.ua"
docker-compose \
  -f docker-compose.yml \
  pull

docker-compose \
  -f docker-compose.yml \
  up -d
