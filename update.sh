echo "Updating the codebase"
git pull origin develop

echo "Stopping the containers"
docker-compose -f docker-compose.prod.yml stop

echo "Removing the containers"
docker-compose -f docker-compose.prod.yml rm -f

echo "Removing the images"
docker-compose -f docker-compose.prod.yml down --rmi all

echo "Building the containers"
docker-compose -f docker-compose.prod.yml up -d