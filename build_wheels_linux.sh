NEW_VERSION="9.4.3.3"
NEW_BRANCH="geo/stem_intermediate_whls"

# Update the build.sh file with version
sed -i "s/^\(export KRATOS_VERSION=\).*$/\1\"$NEW_VERSION\"/" wheels_linux/build.sh

# Update the Dockerfile file with branch
sed -i "s#geo/stem_branch#$NEW_BRANCH#" wheels_linux/Dockerfile

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