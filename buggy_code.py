# This is a new change to trigger the pull request
import os

def check_file(filename):
...
def check_file(filename):
  # This function has a bug. It should check if the file exists *before* trying to read it.
  f = open(filename, "r")
  contents = f.read()
  print("File size is:", len(contents))
  return contents

def get_user_data(id):
    # This function is missing a return statement
    user = "user-" + id
    print("Fetching data for", user)

# Calling a function that doesn't exist
process_data() for 1 
