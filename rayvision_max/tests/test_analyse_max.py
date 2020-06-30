#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import pytest

from rayvision_utils.exception.exception import CGFileNotExistsError


def test_check_path(maya_analyze):
    """Test init this interface.

    Test We can get an ``FileNameContainsChineseError`` if the information is
    wrong.

    """
    maya_analyze.cg_file = "xxx.ma"
    with pytest.raises(CGFileNotExistsError):
        maya_analyze.check_path(maya_analyze.cg_file)
