import json
import logging
import os
import subprocess
import time

from rayvision_max.constants import PACKAGE_NAME

from rayvision_utils import constants
from rayvision_utils import utils
from rayvision_utils.exception.exception import CGFileNotExistsError


class AnalyseMax(object):
    def __init__(self,
                 cg_file,
                 software_version,
                 project_name,
                 plugin_config,
                 workspace=None,
                 max_exe_path=None,
                 renderable_camera=None,
                 render_software="3ds Max",
                 platform="2",
                 logger=None,
                 log_folder=None,
                 log_name=None,
                 log_level="DEBUG"
                 ):
        """Initialize and examine the analysis information.
        Args:
            cg_file (str): Scene file path.
            software_version (str): Software version.
            project_name (str): The project name.
            plugin_config (dict): Plugin information.
            workspace (str): Analysis out of the result file storage path.
            max_exe_path (str): 3ds max exe for analysis.
            renderable_camera (list): Camera to be rendered.
            render_software (str): Software name, Maya by default.
            platform (str): Platform no.
            logger (object, optional): Custom log object.
            log_folder (str, optional): Custom log save location.
            log_name (str, optional): Custom log file name.
            log_level (string):  Set log level, example: "DEBUG","INFO","WARNING","ERROR".
        """
        self.logger = logger
        if not self.logger:
            from rayvision_log.core import init_logger
            init_logger(PACKAGE_NAME, log_folder, log_name)
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=log_level.upper())
        self.cgfile = cg_file
        self.software_version = software_version
        self.project_name = project_name
        self.plugin_config = plugin_config
        self.platform = platform
        self.render_software = render_software
        self.renderable_camera = list(set(renderable_camera)) if renderable_camera is not None else []

        workspace = os.path.join(self.check_workspace(workspace), str(int(time.time()))).replace("\\", "/")
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace

        if max_exe_path:
            self.check_path(max_exe_path)
        self.max_exe_path = max_exe_path

        self.task_json = os.path.join(workspace, "task.json")
        self.tips_json = os.path.join(workspace, "tips.json")
        self.asset_json = os.path.join(workspace, "asset.json")
        self.upload_json = os.path.join(workspace, "upload.json")
        self.tips_info = {}
        self.task_info = {}
        self.asset_info = {}
        self.upload_info = {}
        self.analysemax_py_dir = os.path.dirname(__file__)

    def analyse(self, no_upload=False):
        """Build a cmd command to perform an analysis scenario.

        Args:
            no_upload (bool): Do you not generate an upload,json file.

        Raises:
            AnalyseFailError: Analysis scenario failed.

        """
        self.write_json_file()
        options = {
            'input_cg_file': self.cgfile,
            'tmp_path': self.workspace,
            'cg_version': self.software_version,
            'client_project_dir': self.workspace,
            'ignoreMapFlag': "0",
            'justUploadConfigFlag': "0",
            # 'zip_exe_path': os.path.join(os.path.dirname(__file__), '7z.exe')
        }
        if self.max_exe_path:
            options.updata({'max_exe_path': self.max_exe_path})
        analysemax_exe_path = os.path.join(self.analysemax_py_dir, 'tool', 'analysemax.exe')
        analyse_cmd = '"{}" "{}"'.format(analysemax_exe_path, json.dumps(options).replace('"', '""'))
        self.logger.debug(analyse_cmd)
        analyse_code = self.runcmd(analyse_cmd)
        self.tips_info = utils.json_load(self.tips_json)
        self.asset_info = utils.json_load(self.asset_json)
        self.task_info = utils.json_load(self.task_json)
        if not no_upload:
            self.upload_info = utils.json_load(self.upload_json)
        if analyse_code == 0:
            self.determine_renderable_camera()

    def write_json_file(self):
        """The initialization task.json."""
        constants.TASK_INFO["task_info"]["input_cg_file"] = self.cgfile.replace("\\", "/")
        constants.TASK_INFO["task_info"]["project_name"] = self.project_name
        constants.TASK_INFO["task_info"]["cg_id"] = constants.CG_SETTING.get(self.render_software)
        constants.TASK_INFO["task_info"]["os_name"] = "1"
        constants.TASK_INFO["task_info"]["platform"] = self.platform
        constants.TASK_INFO["software_config"] = {
            "plugins": self.plugin_config,
            "cg_version": self.software_version,
            "cg_name": self.render_software
        }
        utils.json_save(self.task_json, constants.TASK_INFO)
        utils.json_save(self.asset_json, self.asset_info)
        utils.json_save(self.upload_json, self.upload_info)

    def runcmd(self, cmd_str, myshell=True):
        '''Using subprocess.Popen run analyse command'''
        cmd_popen = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=myshell)
        while cmd_popen.poll() is None:
            resultLine = cmd_popen.stdout.readline().strip()
            if resultLine != b'':
                self.logger.debug(resultLine)
        return cmd_popen.returncode

    def check_workspace(self, workspace):
        """Check the working environment.
        Args:
            workspace (str):  Workspace path.
        Returns:
            str: Workspace path.
        """
        if not workspace:
            workspace = os.path.join(os.environ["USERPROFILE"], "renderfarm_sdk")
        else:
            self.check_path(workspace)
        return workspace

    @staticmethod
    def check_path(tmp_path):
        """Check if the path exists."""
        if not os.path.exists(tmp_path):
            raise CGFileNotExistsError("{} is not found".format(tmp_path))

    def determine_renderable_camera(self):
        """determine renderable camera"""
        if self.renderable_camera:
            self.task_info['scene_info_render']['common']['renderable_camera'] = []
            for camera_name in self.renderable_camera:
                if camera_name in self.task_info['scene_info_render']['common']['all_camera']:
                    self.task_info['scene_info_render']['common']['renderable_camera'].append(camera_name)
                else:
                    self.logger.warning('There is no camera in this max scene:{}'.format(camera_name))
        utils.json_save(self.task_json, self.task_info)
