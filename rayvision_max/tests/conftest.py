#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.

References:
    https://docs.pytest.org/en/2.7.3/plugins.html

"""
import pytest

from rayvision_max.analyse_max import AnalyseMax


@pytest.fixture()
def analyze_info(tmpdir):
    """Get user info."""
    cg_file = str(tmpdir.join('jh.max'))
    with open(cg_file, "w"):
        pass
    return {
        "cg_file": cg_file,
        "workspace": str(tmpdir),
        "software_version": "2018",
        "project_name": "Project1",
        "plugin_config": {}
    }


@pytest.fixture()
def maya_analyze(analyze_info):
    """Create an Maya object."""
    return AnalyseMax(**analyze_info)
