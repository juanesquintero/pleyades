docker-compose -f docker-compose.prod.yml stop

git pull origin develop

docker-compose -f docker-compose.prod.yml down --rmi all

docker-compose -f docker-compose.prod.yml stop && docker-compose -f docker-compose.prod.yml rm -f && docker-compose -f docker-compose.prod.yml up -d