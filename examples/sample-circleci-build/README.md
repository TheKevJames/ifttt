# Sample CircleCI Image Build Config
This is a sample CircleCI yaml which uses version 2 of their platform. It should
be copied to `.circleci/config.yml` in the root of your repository.

It uses the `GOOGLE_SERVICE_ASR` environment variable to bake production creds
into your image -- see [the IFTTT readme](/README.md) for more info.

This configuration uses a lovely new feature of CircleCI to get this environment
variable from your GitHub org's general settings (`context: org-global`). This
lets you set this environment variable in a single place on CircleCI
(https://circleci.com/gh/organizations/MY_GITHUB_ORG/settings#contexts) and use
it across all your repos.
