"""Register the nuclear_cascade app and our daemons in a BOINC project (idempotent).

Runs in the official makeproject container, whose Python is 3.5: keep it free of f-strings.
Usage: python3 add_app.py PROJECT_ROOT
"""
import os
import sys
import xml.etree.ElementTree as ET

APP = "nuclear_cascade"
DAEMONS = [
    "script_validator -d 3 --app " + APP + " --credit_from_wu "
    "--init_script \"nah_validate_init result_id runtime files\" --compare_script \"nah_validate_compare\"",
    "script_assimilator -d 3 --app " + APP + " --script \"nah_assimilate wu_id files\"",
]
# Periodic jobs, run by BOINC's own "bin/start --cron" (crontab, every 5 minutes): (cmd, period, disabled)
TASKS = [
    ("nah_generate", "10 min", True),   # off until switched on: it keeps max_in_flight WUs queued
    ("nah_stats hourly", "1 hour", False),
    ("nah_stats daily", "1 day", False),
]


def main(root):
    project_xml = os.path.join(root, "project.xml")
    project = ET.parse(project_xml)
    if not any(a.findtext("name") == APP for a in project.getroot().iter("app")):
        app = ET.SubElement(project.getroot(), "app")
        ET.SubElement(app, "name").text = APP
        ET.SubElement(app, "user_friendly_name").text = "Nuclear@Home cascade"
        project.write(project_xml)
    config_xml = os.path.join(root, "config.xml")
    config = ET.parse(config_xml)
    daemons = config.getroot().find("daemons")
    for daemon in list(daemons):  # replace our daemons, so a changed command line takes effect
        if "--app " + APP in (daemon.findtext("cmd") or ""):
            daemons.remove(daemon)
    for cmd in DAEMONS:
        ET.SubElement(ET.SubElement(daemons, "daemon"), "cmd").text = cmd
    tasks = config.getroot().find("tasks")
    if tasks is None:
        tasks = ET.SubElement(config.getroot(), "tasks")
    for task in list(tasks):  # replace ours, keep BOINC's own tasks
        if (task.findtext("cmd") or "").startswith("nah_"):
            tasks.remove(task)
    for cmd, period, disabled in TASKS:
        task = ET.SubElement(tasks, "task")
        ET.SubElement(task, "cmd").text = cmd
        ET.SubElement(task, "period").text = period
        ET.SubElement(task, "output").text = cmd.replace(" ", "_") + ".out"
        if disabled:
            ET.SubElement(task, "disabled").text = "1"
    config.write(config_xml)


if __name__ == "__main__":
    main(sys.argv[1])
