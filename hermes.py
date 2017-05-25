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



def read_job_list(jenkins_url, view_name):
    url = jenkins_url + "/view/" + view_name + "/api/json?pretty=true"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return (job["name"] for job in data["jobs"])



def parse_number(line):
    parsed = re.match(r"[a-zA-Z]+: ([0-9.]+)", line)
    return float(parsed.group(1))



def read_style_stat(jenkins_url, view_name, job_name, names):
    url = jenkins_url + "/view/" + view_name + "/job/" + job_name + "/lastSuccessfulBuild/artifact/tmp/en-US/txt/style.txt"
    fin = urllib.urlopen(url)
    content = fin.read().split("\n")
    stat = {}
    stat["job_name"] = job_name
    for line in content:
        line = line.strip()
        for name in names:
            if line.startswith(name + ": "):
                stat[name] = parse_number(line)
            
        #print line
    return stat



"""
Kincaid: 9.4
        ARI: 10.7
        Coleman-Liau: 12.5
        Flesch Index: 55.7/100
        Fog Index: 12.0
        Lix: 44.6 = school year 8
        SMOG-Grading: 11.2
"""



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

    names = ["Kincaid", "ARI"]
    job_list = read_job_list(args.jenkins_url, args.view)
    for job in job_list:
        stat = read_style_stat(args.jenkins_url, args.view, job, names)
        print(stat)
    
    
    #fig = create_graph()
    #save_graph(fig, IMAGE_FILE)

# Vstupni bod
if __name__ == "__main__":
    main()

