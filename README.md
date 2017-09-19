# If This Then That, Dev Style
The [IFTTT project](https://ifttt.com/) is an great resource with a simple idea:

> > if {trigger condition occurs} then {do result action}

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
