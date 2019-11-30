# Contributing to NBoost

First of all, thanks for being willing to contribute to NBoost, we love to learn best practice from the community.

## Making Commits 

Contributions are greatly appreciated! You can make corrections or updates and commit them to NBoost. Here are the steps:

1. Create a new branch, say `fix-nboost-typo-1`
2. Fix/improve the codebase
3. Commit the changes. Note the **commit message must follow [the naming style](./CONTRIBUTING.md#commit-message-naming)**, say `Fix/Model-bert: improve the readability and move sections`
4. Make a pull request. Note the **pull request must follow [the naming style](./CONTRIBUTING.md#commit-message-naming)**. It can simply be one of your commit messages, just copy paste it, e.g. `Fix/Model-bert: improve the readability and move sections`
5. Submit your pull request and wait for all checks passed (usually 10 minutes)
    - Coding style
    - Commit and PR styles check
    - All unit tests
6. Request reviews from one of the developers from our core team.
7. Merge!

## Table of Content

* [Commit Message Naming](#commit-message-naming)
* [Merging Process](#merging-process)
* [Release Process](#release-process)
  - [Major and minor version increments](#major-and-minor-version-increments)
* [Testing Locally](#testing-locally)
* [Interesting Points](#intersting-points)
  
## Commit Message Naming

To help everyone with understanding the commit history of NBoost, we employ [`commitlint`](https://commitlint.js.org/#/) in the CI pipeline to enforce the commit styles. Specifically, our convention is:

```text
Type/Scope: subject
```

where `type` is one of the following:

- build
- ci
- chore
- docs
- feat
- fix
- perf
- refactor
- revert
- style
- test

`scope` is optional, represents the module your commit working on.

`subject` explains the commit.

As an example, a commit that implements a new encoder should be phrased as:
```text
Fix/Model-bert: improve the readability and move sections
``` 

## Merging Process

A pull request has to meet the following conditions to be merged into master:

- Coding style check (PEP8, via Codacy)
- Commit style check (in CI pipeline via Drone.io)
- Unit tests (via Drone.io)
- Review and approval from a Koursaros team member.