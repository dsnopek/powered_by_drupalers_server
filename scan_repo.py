
import argparse
import git
import csv
import os

def count_author_lines_in_repo(repo, filepath):
    author_count = {}
    blame = repo.blame('HEAD', filepath)
    for commit, lines in blame:
        if commit.author.email not in author_count:
            author_count[commit.author.email] = 0
        author_count[commit.author.email] += len(lines)
    return author_count

def sum_dicts(*args):
    result = {}
    for d in args:
        for k, v in d.items():
            if k not in result:
                result[k] = 0
            result[k] += v
    return result

def count_author_lines_in_directory(repo_path):
    repo = git.Repo(repo_path)
    author_counts = []

    # Walk the repo, counting the author of individual lines.
    for (dirpath, dirnames, filenames) in os.walk(repo_path):
        # Get the dirpath relative to the top of repo
        if dirpath[:len(repo_path)] == repo_path:
            dirpath = dirpath[len(repo_path)+1:]

        # Skip the .git directory
        if dirpath[:4] == '.git':
            continue

        for filename in filenames:
            # Skip binary files.
            if any(filename.endswith(x) for x in ('.jpg', '.jpeg', '.gif', '.png')):
               continue

            filepath = os.path.join(dirpath, filename)
            author_counts.append(count_author_lines_in_repo(repo, filepath))

    return sum_dicts(*author_counts)

def calculate_author_percent(author_count):
    total_count = sum(author_count.values())
    return dict([(author, float(count) / total_count * 100) for author, count in author_count.items()])

def dict_zip(*args):
    for i in set(args[0]).intersection(*args[1:]):
        yield (i,) + tuple(d[i] for d in args)

def write_csv(filepath, header, rows):
    with open(filepath, 'wb') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header.
        writer.writerow(header)
        # Write the data.
        for row in rows:
            writer.writerow(list(row))

def main():
    parser = argparse.ArgumentParser(description='Calculate the percentage of the source code written by each author.')
    parser.add_argument('git-repo', nargs=1)
    parser.add_argument('output-csv', nargs=1)
    args = vars(parser.parse_args())

    repo_path = args['git-repo'][0]
    csv_path = args['output-csv'][0]

    author_counts = count_author_lines_in_directory(repo_path)
    author_percent = calculate_author_percent(author_counts)

    # Convert percents to strings with only 2 decimal places.
    author_percent = dict([(author, "%.2f" % percent) for author, percent in author_percent.items()])

    write_csv(csv_path, ['author','lines','percent'], dict_zip(author_counts, author_percent))

if __name__ == "__main__": main()
