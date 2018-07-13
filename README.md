# Real-world Bazel
[Bazel][bazel] build files collected from real-world GitHub projects. Makes finding examples and inspiration of build rule usage much easier!

## Using

Simply [download the latest .zip file](https://github.com/cgbystrom/real-world-bazel/releases) of all collected BUILD files and use your favorite code search tool.

## Rationale
For anyone outside Google, [Bazel][bazel] is quite a new build tool. It was open-sourced in 2015 and has since gained more and more traction. But being a new tool also means documentation, best practices and examples are not as easy to come by compared to other, more established build tools.

One of the things I've found most helpful in learning Bazel has been looking at other real-world usages of it. Either by googling or searching GitHub projects.
This has been working okay-ish, but GitHub's code search can definitely be lacking at times when you just want to find that example snippet.

So instead of relying on their search I figured it would be much easier to just download every public, Bazel-based GitHub project out there. In that way, I could just `grep` and search for whatever build rule usage I wanted in mere seconds.

## How this was collected

To actually find every Bazel based project on Github, first step would be to reliable detect Bazel usage.
A very simple way of doing this is just checking for the presence of a `WORKSPACE` file in the root directory.
While not 100% perfect, it's definitely good enough.

Second problem is scanning every repository for the presence of that file. Doing that through just brute force or GitHub search isn't feasible.
Fortunately, Google offers the [entire content of GitHub as a public dataset][github-dataset] with BigQuery.

To find every GitHub project that contains a WORKSPACE file in the root, you can issue this query:
```
SELECT
  repo_name
FROM
  [bigquery-public-data:github_repos.files]
WHERE
  path == "WORKSPACE"
GROUP BY
  repo_name
```

Leaving you with a long list of repositories. And despite the amount of data scanned, the above query cost less than $1.

In addition of identifying Bazel based repos I also wanted the number of stars for each to help filter the list further.
Since the size was quite manageable (less than 1000 repos) I just grabbed this from the public GitHub API with a script.
To avoid forks and abandoned projects, any repo below 10 stars was filtered out*.

So armed with a list of repos and stars I put together another script for actually downloading every repo.
It simply downloads and then removes any non-Bazel related files to keep the size down.
After a good 45 minutes what is left are only Bazel BUILD files from every public GitHub project out there :)



*) I later learned you can collect this in BigQuery as well since they offer _two_ datasets. Oh well, next time maybe!

[bazel]: http://bazel.build/
[github-dataset]: https://cloud.google.com/bigquery/public-data/github
