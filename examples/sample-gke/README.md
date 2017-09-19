# Sample Kubernetes (GKE) Deployment Config
This is a bunch of sample files for deploying your IFTTT image with Kubernetes
on GKE. See [the sample CircleCI configuration](/examples/sample-circleci-build)
for the build/push-to-gcr part of this.

The [deployment.yaml file](deployment.yaml) shows the actual container
configuration.

The [secrets.yaml file](secrets.yaml) shows the secret parts of the
configuration. No, I didn't accidentally commit my own secret values the first
time I made this example file, why do you ask?

The [circleci.yml file](circleci.yml) shows a sample chunk of a CircleCI v2
workflow for updating the image of your kubernetes deployment whenever you
commit to master. Yay Continuous Deployment! As with
[the sample CircleCI configuration](/examples/sample-circleci-build), this uses
org-wide secrets to help you avoid configuration soup.
