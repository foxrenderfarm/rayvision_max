# -*- coding: utf-8 -*-

from rayvision_max.analyse_max import AnalyseMax

analyze_info = {
    "cg_file": r'D:\houdini\cg_file\max2018.max',
    "software_version": "2018",
    "project_name": "Project1",
    "workspace": r"C:\workspace\max",
    "plugin_config": {},
    "renderable_camera": ["PhysCamera001"],
}

AnalyseMax(**analyze_info).analyse()
