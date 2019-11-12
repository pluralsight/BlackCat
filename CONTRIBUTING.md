# Contributing to BlackCat

## Code of Conduct

Help me keep the discussion open and inclusive. Please read and follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

## Submitting a Pull Request (PR)

Before you submit your Pull Request (PR) consider the following guidelines:

1. Fork the blackcat repository.  
2. Make your changes, including appropriate test cases.
3. Ensure all tests pass (see [Testing](#Testing))
4. Update CHANGELOG.md (under the latest `UNRELEASED` build) with noteworthy changes
5. Commit and push your changes using a descriptive commit message.
6. Submit a PR to our master branch.  

**In order to preserve sanity, please ensure your PR follows the guidelines set in the template, and that all boxes are checked before submitting. Additionally, please _do not_ squash commits before
submitting.**
  
## Testing
To run tests, simply execute `run_test.sh`. The two test suites we run are unit tests and linting tests.
Our linting is basically the vanilla [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/) outside of
slightly longer lines (max 120 chars)
  

## Commits
Commit messages should be descriptive and explain changes made. Please avoid squashing your commits, as that deletes
part of the historical record. If multiple changes are included in a commit, consider  splitting it into multiple
smaller commits or adding a list in the message body. Please keep commit bodies short if possible.
