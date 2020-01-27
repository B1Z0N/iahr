export DOCKER_HOST="ssh://kraftwerk28.pp.ua"

docker-compose \
  -f docker-compose.yml \
  -f docker-compose.deploy.yml \
  pull

docker-compose \
  -f docker-compose.deploy.yml \
  up -d
