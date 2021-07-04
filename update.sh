docker stop satsuki
docker rm satsuki
docker pull ghcr.io/being24/satsuki:latest
docker run -d -v satsuki-data:/opt/satsuki/data --network postgre_default --env-file .env --restart=always --name=satsuki ghcr.io/being24/satsuki