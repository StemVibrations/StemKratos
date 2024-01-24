# Start docker deamon
sudo service docker start

# Build docker image
docker build -t stemkratos:1.0 -f ./wheels_linux/Dockerfile ./wheels_linux

# Run docker image
docker run stemkratos:1.0

# get docker id
container_id=$(docker ps -q -a --filter "ancestor=stemkratos:1.0")

# copy wheels to host
docker cp "${container_id}:/data_swap_guest" ./wheels_linux/wheels