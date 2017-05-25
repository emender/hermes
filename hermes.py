import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import json
import urllib
import re
import argparse

IMAGE_FILE = "test.png"



def create_graph():
    fig = plt.figure()
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    plt.plot(x, y)
    plt.xlabel("x")
    plt.ylabel("sin(x)")
    return fig



def save_graph(fig, imageFile):
    plt.savefig(imageFile)



def job_list_url(jenkins_url, view_name):
    return jenkins_url + "/view/" + view_name + "/api/json?pretty=true"



def computed_stat_url(jenkins_url, view_name, job_name):
    return jenkins_url + "/view/" + view_name + "/job/" + job_name + "/lastSuccessfulBuild/artifact/tmp/en-US/txt/style.txt"



def read_job_list(jenkins_url, view_name):
    url = job_list_url(jenkins_url, view_name)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return (job["name"] for job in data["jobs"])



def parse_number(line):
    parsed = re.match(r"[- a-zA-Z]+: ([0-9.]+)", line)
    return float(parsed.group(1))



def parse_last_number(line):
    parsed = re.match(r"[- a-zA-Z]+: .* ([0-9.]+)$", line)
    return int(parsed.group(1))



def parse_book_name(job_name):
    if job_name.startswith("doc-") and job_name.endswith(" (style-checker)"):
        updated_name = job_name[len("doc-"): -len(" (style-checker)")]
        if updated_name:
            return updated_name.replace("-", " ").replace("_", " ")
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
            
        #print line
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
    for job in job_list:
        stat = read_style_stat(args.jenkins_url, args.view, job, names)
        print(stat)
    
    
    #fig = create_graph()
    #save_graph(fig, IMAGE_FILE)

# Vstupni bod
if __name__ == "__main__":
    main()

