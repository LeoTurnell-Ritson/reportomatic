# ReportOmatic

ReportOmatic is a CLI utility for generating opinionated reports for both GitLab and GitHub repositories in the same Markdown format. 

## Features

- Generate list of active issues
- Generate list of active pull/merge requests

## Usage

To generate a report of active issues for a given repository, use the following command:
```bash
reportomatic <repository-url> issues
```

Similarly to generate a report of active pull/merge:
```bash
reportomatic <repository-url> pulls
```
