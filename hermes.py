import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json
import urllib
import re
import argparse

IMAGE_FILE = "test.png"



def create_graph(graph_label, y_axis_label, labels, values):
    N = len(values)
    indexes = np.arange(N)

    fig = plt.figure()
    plt.xlabel("guide name")
    plt.ylabel(y_axis_label)
    plt.grid(True)
    plt.xticks(indexes, labels)
    locs, plt_labels = plt.xticks()
    plt.setp(plt_labels, rotation=90)
    plt.bar(indexes, values, 0.80, color='yellow', edgecolor='black', label=graph_label)
    #plt.legend(loc='lower right')
    for tick in plt_labels:
        tick.set_horizontalalignment("left")
        tick.set_verticalalignment("top")
    plt.tick_params(axis='x', which='major', labelsize=10)
    fig.subplots_adjust(bottom=0.4)
    fig.suptitle(graph_label)
    return fig



def save_graph(fig, imageFile):
    plt.savefig(imageFile, facecolor=fig.get_facecolor())



def generate_graph(product, name, stats):
    labels = [key for key,val in stats.items()]
    values = [val[name] for key,val in stats.items()]
    fig = create_graph(product, name, labels, values)
    save_graph(fig, name + ".png")



def job_list_url(jenkins_url, view_name):
    return jenkins_url + "/view/" + view_name + "/api/json?pretty=true"



def computed_stat_url(jenkins_url, view_name, job_name):
    return jenkins_url + "/view/" + view_name + "/job/" + job_name + "/lastSuccessfulBuild/artifact/tmp/en-US/txt/style.txt"



def read_job_list(jenkins_url, view_name):
    url = job_list_url(jenkins_url, view_name)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    job_list = [job["name"] for job in data["jobs"]]
    list.sort(job_list)
    return job_list



def read_product(job_list):
    for job in job_list:
        if job.startswith("doc-"):
            splitted = job.split("-")
            return splitted[1].replace("_", " ")
    return None



def parse_number(line):
    parsed = re.match(r"[- a-zA-Z]+: ([0-9.]+)", line)
    return float(parsed.group(1))



def parse_last_number(line):
    parsed = re.match(r"[- a-zA-Z]+: .* ([0-9.]+)$", line)
    return int(parsed.group(1))



def find_space_near_middle(s):
    middle = len(s)/2
    for i in range(middle-1):
        if s[middle+i] == " ":
            return middle+i
        if s[middle-i] == " ":
            return middle-i
    return None



def wrap_near_middle(s):
    space = find_space_near_middle(s)
    if space:
        return s[:space] + "\n" + s[space+1:]
    else:
        return s



def parse_book_name(job_name):
    if job_name.startswith("doc-") and job_name.endswith(" (style-checker)"):
        splitted = job_name.split("-")
        updated_name = job_name[len("doc-"): -len(" (style-checker)")]
        if updated_name:
            splitted = updated_name.split("-")
            joined = str.join("-", splitted[2:]).replace("_", " ")
            wrapped = wrap_near_middle(joined)
            return wrapped
        else:
            return None
    else:
        return None



def read_style_stat(jenkins_url, view_name, job_name, names):
    url = computed_stat_url(jenkins_url, view_name, job_name)
    fin = urllib.urlopen(url)
    content = fin.read().split("\n")
    stat = {}
    stat["job_name"] = job_name
    stat["book_name"] = parse_book_name(job_name)
    for line in content:
        line = line.strip()
        for name in names:
            if line.startswith(name + ": "):
                stat[name] = parse_number(line)
            if line.startswith("Lix: "):
                stat["school year"] = parse_last_number(line)
    return stat



def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jenkins-url", help="URL to Jenkins instance")
    parser.add_argument("-v", "--view", help="Jenkins view with job for doc statistic")
    return parser.parse_args()



def check_args(args):
    if not args.jenkins_url:
        exit("-j/--jenkins-url argument is mandatory")
    if not args.view:
        exit("-v/--view argument is mandatory")



def main():
    args = read_args()
    check_args(args)

    names = ["Kincaid", "ARI", "Coleman-Liau", "Flesch Index", "Fog Index", "Lix", "SMOG-Grading"]
    job_list = read_job_list(args.jenkins_url, args.view)
    product = read_product(job_list)
    stats = {}
    for job in job_list:
        stat = read_style_stat(args.jenkins_url, args.view, job, names)
        stats[stat["book_name"]] = stat

    names.append("school year")
    for name in names:
        generate_graph(product, name, stats)



# Vstupni bod
if __name__ == "__main__":
    main()

