from github import Github
import streamlit as st

GITHUB = st.secrets["GITHUB"]

def get_github_all_files(repo):
    g = Github(GITHUB)
    #repo = g.get_repo("swardley/Research2022")
    repo = g.get_repo(repo)
    contents = repo.get_contents("")
    return (contents)

def get_github_wm_file(filename):
    contents = repo.get_contents(filename)
    return (contents)
