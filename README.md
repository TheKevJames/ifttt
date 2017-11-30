# If This Then That, Dev Style
The [IFTTT project](https://ifttt.com/) is an great resource with a simple idea:

> "if {trigger condition occurs} then {do result action}"

This project exists to bring the IFTTT mindset to more places -- specifically,
to cover any tasks that fit the above mindset but can't/shouldn't/won't be run
on the actual IFTTT platform for whatever reason. Some reasons that prompted me
to create this:
- secret management
- cleaner/better infrastructure integration

Even _more_ specifically, this project was born out of the need to manage
production kubernetes deployments based on changing datastore entries for
customers such as enabling/disabling feature flags and changing allocated
resources.

## How Do I Use This Thing?
Well, mostly that depends how you _want_ to use it. Here's the parts you
absolutely need to have:
- a Dockerfile that uses the IFTTT base image `thekevjames/ifttt`. You can find
the list of all available tags [on DockerHub](https://hub.docker.com/r/thekevjames/ifttt/tags/)
but here's the general idea: every single commit is available as a tag, as is
every branch's most recent commit. You can use `:${BRANCH}-${HASH}`,
`:${BRANCH}`, or `:latest` -- my personal recommendation is to pin to a specific
commit on master so you can manage this project as a dependency rather than have
it change underneath you.
- an `actions` folder, containing all the stuff you want to do when your
triggers happen. If any of these actions require dependencies not included in
this repository, make sure you install them in your `Dockerfile`!
- relatedly, an `ifttt.yaml` configuration file defining when and how to run
those actions. This file is super important, so it gets its own README section
below.

You can find an example project which you probably want to copy into your own
repo in [the examples/sample-repo subdirectory](examples/sample-repo).

### Configuring `ifttt.yaml`
I aim to keep the configuration as simple as possible; if you have any ideas for
how to make it even better, please let me know! You can find the
[sample ifttt.yaml file here](examples/sample-repo/ifttt.yaml).

The configuration yaml is just a list of `if`s and `then`s ("watches"). Each
watch has three or four keys: `name`, `watch`, `if` (optional), and `then`.
Here's an example:

```yaml
- name: sample watch configuration
  watch:
    source: datastore
    kind: UserData
    field: number_of_aardvarks_owned
  if: value < 42
  then:
    - send-slack-notif -t "{value} is not enough aardvarks!"
    - buy-aardvarks --user {id} --amount 1337
    - send-slack-notif -t "now THAT is enough aardvarks :)"
```

I'm hoping this is completely straightforward; but let's go through the
nitty-gritty details anyway.

#### name
This is basically just an identifier. You'll see it in logs, if you ever read
those. It doesn't really do anything interesting. Moving on...

#### watch
This is where you configure what "thing" should be watched for changes. This is
configured as a dictionary, with the `source` field specifying the type of
"thing" to-be-watched. Different sources require code changes -- I am more than
happy to accept PRs that introduce new ones, but otherwise I'll mostly be
implementing these as I need them / am interested in playing with something new
/ feel like it.

If your `source` is set to "datastore", you need to additionally configure the
`kind` and `field` keys. The former tells IFTTT which datastore kind to watch
and the `field` tells IFTTT which field to check for changes. Every record in
the kind will be checked. You can also use `aggregate: sum` to apply your watch
as an aggregate over the sum of each record. The value of this key can be any
arbitrary python code to be applied.

For example, you could set:

```yaml
- name: notify on insane questions
  watch:
    source: datastore
    kind: Question
    field: question_importance
    aggregate: max
  if: value > 9000
  then:
    - send-slack-notif -t "The most important question ({value}) is over 9000!"
```

An `aggregate` can also include some `context` which is used to sub-divide
aggregations. For example, if you have a datastore Kind containing counts of
items of varying colors, you may set:

```yaml
- name: count items by color
  watch:
    source: datastore
    kind: Item
    field: count
    aggregate:
      expression: sum
      context: color
  then:
    - send-slack-notif -t "There are {{value}} items colored {{context}}"
```

#### if
The `if` field is an arbitrary block of python code which will be used to
determine whether your actions should be run. If the code block returns a truthy
value, the `then` block will be executed.

When writing this section, you have access to the `id` of the record being
evaluated, the `prev`ious value of the watched field for that record, and the
`curr`ent value of the same field.

```python
should_i_run_actions = (lambda id, prev, curr: {id field goes here})(...)
```

The `if` field defaults to `prev != curr`, ie. running on each change to the
field.

There's a bit of a caveat here that you should be aware of! Datastore records
don't need to have all fields set, so there's a functional difference between
a field being `None` versus it being `False` or `0` or `""` or what-have-you.
If your watch cares about that distinction, you may need to keep this in mind!

#### then
The `then` field is an *ordered* list of commands to be run, if the watch
trigger occurs. Anything in this list is run in a subshell of your IFTTT image.
Most likely, you'll want to write some custom scripts and throw them in your
`actions` folder. Make sure you include any dependencies of those new actions
in your image!

I've included `send-slack-notif` by default, since I am a big fan of having a
notification stream of everything important. If you want to use that
notification script, you'll need to have `SLACK_WEBHOOK_URL` and
`SLACK_CHANNEL` in your IFTTT image's environment, either by baking them into
the image or setting them at runtime. You can get a webhook URL by creating a
[custom integration](https://slack.com/apps/A0F7XDUAZ-incoming-webhooks).

You have access to the record `{id}` and `{value}` in each of these actions.
For example:

```yaml
then:
  - send-slack-notif -t "{id} had its 'number of cows' field changed to {value}"
```

### Actually Building An Image
Not much to say here! The base image is set up with `ONBUILD` commands, so if
you follow the outline described above (and in the [sample repo](examples/sample-repo))
then everything should Just Work™.

However you do your image builds should run

```bash
docker build --build-arg GOOGLE_SERVICE_ASR=${GOOGLE_SERVICE_ASR} -t ifttt .
```

Your `GOOGLE_SERVICE_ASR` variable can be set by [grabbing a service key from gcloud](TODO)
and base64 encoding it.

```bash
export GOOGLE_SERVICE_ASR=$(echo service.json | base64)
```

Sadly this needs to be done at build time rather than runtime so we can build
the json file into the image. Personally, I much prefer setting this in the
environment rather than copying in the file itself to help deal with keeping
secrets out of git -- if you have some different workflow for this, you can
override the `/run/service-asr.json` file in your image build.

### What About Deployment?
The possibilities are pretty much endless here. Here's whats important:
- build your image and put it... somewhere. [dockerhub](https://hub.docker.com/)
is cool, [google container registry](gcr.io) is as well, the possibilities are
absolutely limitless (read: at least two)! Make sure you don't make the image
public if your image has any secrets baked into it.
    - if you use [CircleCI](https://circleci.com/), which is an awesome CI
    system, you can check out
    [the sample CircleCI configuration](examples/sample-circleci-build).
- deploy your image! Make sure you have all the necessary environment variables
set for the features you are using.
    - if you want to deploy to a Kubernetes cluster, you can check out
    [the sample Kubernetes-on-GKE-deployed-with-CircleCI configuration](examples/sample-gke)

### How About Running This Ad-Hoc?
You can build and run this with standard docker commands pretty damn easily.
Here's how you get started:

```bash
docker build --build-arg GOOGLE_SERVICE_ASR=${GOOGLE_SERVICE_ASR} -t ifttt .
docker run -it -e GCLOUD_PROJECT=my-gcloud-project -e DEBUG=true ifttt
```

You can find an annotated list of all the possible environment variables in the
[sample kubernetes deployment definition](examples/sample-gke/deployment.yaml).
