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
    "script_assimilator -d 3 --app " + APP + " --script \"nah_assimilate wu_name files\"",
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
    present = set((d.findtext("cmd") or "").strip() for d in daemons.iter("daemon"))
    for cmd in DAEMONS:
        if cmd not in present:
            ET.SubElement(ET.SubElement(daemons, "daemon"), "cmd").text = cmd
    config.write(config_xml)


if __name__ == "__main__":
    main(sys.argv[1])
