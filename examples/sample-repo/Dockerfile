# Pinning to a version other than `latest` is even better!
FROM thekevjames/ifttt:latest

# If your actions require new dependencies, make sure to install them.
RUN apk add --no-cache g++

# The `ping-domain.sh` sample action uses the `DOMAIN` variable as a constant.
# You can set this in your image environment however you want... if you want to
# bake it into your image, go right ahead!
ENV DOMAIN example.com
# That said, many of these variables probably make more sense as runtime flags
# (ie. `docker run -e DOMAIN=example.com ifttt` or set however you are running
# this project). YMMV!
