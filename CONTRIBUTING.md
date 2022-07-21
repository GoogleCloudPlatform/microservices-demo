# How to Contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

### Fork

In the interest of keeping this repository clean and manageable, you should
work from a fork. To create a fork, click the 'Fork' button at the top of the
repository, then clone the fork locally using `git clone
git@https://github.com/<YOUR_GITHUB_HANDLE>/microservices-demo`.

You should also add this repository as an "upstream" repo to your local copy,
in order to keep it up to date. You can add this as a remote like so:

`git remote add upstream https://github.com/signalfx/microservices-demo.git`

Verify that the upstream exists:

`git remote -v`

To update your fork, fetch the upstream repo's branches and commits, then merge
your `main` with upstream's `main`:

```
git fetch upstream
git checkout main
git merge upstream/main
```

Remember to always work in a branch of your local copy, as you might otherwise
have to contend with conflicts in `main`.


## Creating a PR

Checkout a new branch, make modifications, build locally, and push the branch to your fork
to open a new PR:

```shell
$ git checkout -b myfeature
# edit
# verify that all applications are running well and emitting expected telemetry
$ git add .
$ git commit -m "My commit mesage"
$ git push --set-upstream origin myfeature
```
