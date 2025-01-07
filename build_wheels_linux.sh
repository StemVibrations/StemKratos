NEW_VERSION="9.5.0.6"
NEW_BRANCH="geo/linear_elastic_strategy"

# Update the build.sh file with version
sed -i "s/^\(export KRATOS_VERSION=\).*$/\1\"$NEW_VERSION\"/" wheels_linux/build.sh

# Update the Dockerfile file with branch
sed -i "s#geo/stem_branch#$NEW_BRANCH#" wheels_linux/Dockerfile

# Build docker image
docker build -t stemkratos:1.2 -f ./wheels_linux/Dockerfile ./wheels_linux

# Run docker image
docker run -v $(pwd)/wheels_linux/wheels:/data_swap_guest stemkratos:1.2

# get docker id
container_id=$(docker ps -q -a --filter "ancestor=stemkratos:1.2")

# copy wheels to host
docker cp "${container_id}:/data_swap_guest" ./wheels_linux/wheels