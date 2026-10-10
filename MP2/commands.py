###################################################################
# This is a list of all commands you need to run for MP2 on Colab.
###################################################################

# Clone the team GitHub repository in a fresh runtime, or update an existing clone.
import os
%cd /content
if not os.path.exists("CS598JBR-Team-17"):
    !git clone https://github.com/RLin8103/CS598JBR-Team-17.git
%cd /content/CS598JBR-Team-17
!git pull --ff-only
%cd /content/CS598JBR-Team-17/MP2

# Dataset generated in MP1 for Team 17.
input_dataset = "selected_humaneval_126511212782177902231984929477270226141.jsonl"

# Set up requirements for model prompting
! bash -x setup_models.sh

# Seed generated in MP1.
seed = "126511212782177902231984929477270226141"
task_1_vanilla_json = "task_1_" + seed + "_vanilla.jsonl"
task_1_crafted_json = "task_1_" + seed + "_crafted.jsonl"
task_2_vanilla_json = "task_2_" + seed + "_vanilla.jsonl"
task_2_crafted_json = "task_2_" + seed + "_crafted.jsonl"

# Prompt the models, you can modify `MP2/task_1.py, MP2/task_2.py`
# The {input_dataset} is the JSON file consisting of 20 unique programs for your group that you generated in MP1 (selected_humaneval_[seed].jsonl)
! python3 task_1.py {input_dataset} "deepseek-ai/deepseek-coder-6.7b-instruct" {task_1_vanilla_json} "True" |& tee task_1_vanilla.log
! python3 task_1.py {input_dataset} "deepseek-ai/deepseek-coder-6.7b-instruct" {task_1_crafted_json} "False" |& tee task_1_crafted.log
! python3 task_2.py {input_dataset} "deepseek-ai/deepseek-coder-6.7b-instruct" {task_2_vanilla_json} "True" |& tee task_2_vanilla.log
! python3 task_2.py {input_dataset} "deepseek-ai/deepseek-coder-6.7b-instruct" {task_2_crafted_json} "False" |& tee task_2_crafted.log

# Commands to generate coverage reports

%cd /content/CS598JBR-Team-17

# Push all necessary files (for example, the generated JSONL and log files) to GitHub.
