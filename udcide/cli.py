import os
import sys
module_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(module_path)

import logging
import random
import string
import tempfile
from subprocess import PIPE, STDOUT, CalledProcessError, run
from tempfile import TemporaryDirectory

import click
from dialog import Dialog
from quark import config
from quark.freshquark import download
from quark.Objects.quark import Quark
from quark.Objects.quarkrule import QuarkRule

from udcide.main import UDcide
from udcide.report import Crime


@click.command()
@click.argument('apk_path', type=click.Path(exists=True, dir_okay=False, readable=True))
def entry_point(apk_path):
    def find_executable(executable, path=None):
        if not path:
            path = os.environ['PATH']

        paths = path.split(os.pathsep)

        for p in paths:
            full_path = os.path.join(p, executable)
            if os.path.exists(full_path):
                return full_path

    def exec_tool(command, msg, input=None, timeout=None):
        try:
            process = run(command, stderr=STDOUT, stdout=PIPE,
                          input=input, check=True, timeout=timeout)
            logger.info(process.stdout.decode())
            process.check_returncode()
        except CalledProcessError:
            dialog.gauge_stop()
            dialog.msgbox(msg)
            logger.error(msg)
            return False

        return True

    def generate_random_string(length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    # Setup logger
    logger = logging.getLogger('UDcide-dlog')
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler('udcide.log', 'a')
    logger.addHandler(ch)

    dialog = Dialog(autowidgetsize=True)
    dialog.set_background_title('UDcide')
    dialog.infobox('Detecting dependencies...')

    # Find tools in $PATH
    tools = ['apktool', 'jarsigner', 'keytool']
    tool_paths = dict()
    for tool in tools:
        path = find_executable(tool)
        if path:
            tool_paths[tool] = path

    missed_tools = [tool for tool in tools if tool not in tool_paths]
    if missed_tools:
        msg = f'Cannot found {",".join(missed_tools)} in PATH.'
        dialog.msgbox(msg)
        logger.error(msg)
        return

    # Download Quark Rules
    if not os.path.exists(config.DIR_PATH):
        dialog.infobox('Downloading Quark rules...')
        logger.info('Downloading Quark rules.')
        download()

    # Run Quark analysis
    logger.info('Analysing APK with Quark-Engine.')
    dialog.gauge_start('Analysing with Quark-Engine...')
    rule_dir = config.DIR_PATH
    quark = Quark(apk_path)
    rule_list = [x for x in os.listdir(rule_dir) if x.endswith('json')]

    factor = 100/len(rule_list)
    behavior_list = []
    for index, rule in enumerate(rule_list):
        rule_path = os.path.join(rule_dir, rule)
        checker = QuarkRule(rule_path)

        dialog.gauge_update(int(factor*index), checker.crime, True)

        quark.run(checker)
        parents = quark.quark_analysis.level_5_result
        if parents:
            behavior_list.append(Crime(checker.crime, list(
                (str(p.full_name) for p in parents))))

    dialog.gauge_stop()

    # Select behavior
    logger.info('Waiting for user to select behavires.')

    code, tags = dialog.checklist('Select behaviores to disable.', choices=[
                                  (c.description, '', False) for c in behavior_list])
    if code == dialog.CANCEL:
        logger.info('Canceled by user.')
        return

    if not tags:
        dialog.msgbox('You have seleceted nothing to disalbe.')
        logger.warning('Nothing seleceted by user.')
        return

    logger.info(f'Selected: {tags}')

    selected_list = []
    for behavior in behavior_list:
        if behavior.description in tags:
            selected_list.extend(behavior.sequences)

    smali_dir = TemporaryDirectory('udcide').name
    apk_out = os.path.join('out', os.path.basename(apk_path))

    TOTAL_STAGE = 4
    WEIGHT = 100/TOTAL_STAGE
    # Unpack APK
    dialog.gauge_start('Unpacking APK...')
    logger.info('Unpacking APK with apktool.')

    command = [
        tool_paths['apktool'],
        'd',
        '-r',
        '-f',
        '-o',
        smali_dir,
        apk_path
    ]

    if not exec_tool(command, 'Error on unpacking APK', input=b'b'):
        return

    # Modify APK
    dialog.gauge_update(int(WEIGHT*1), 'Modifying APK...', True)
    logger.info('Modifying APK.')

    udcide = UDcide(apk_path, os.path.join(smali_dir, 'smali'))
    udcide.batch_disable(selected_list)

    # Pack APK
    dialog.gauge_update(int(WEIGHT*2), 'Repacking APK...', True)
    logger.info('Repacking APK with APKtool.')

    command = [
        tool_paths['apktool'],
        "b",
        "-o",
        apk_out,
        smali_dir
    ]

    if not exec_tool(command, 'Error on repacking APK', input=b'b'):
        return

    # Sign APK
    # Generate random keystore
    logger.info('Generating random keystore.')
    dialog.gauge_update(int(WEIGHT*3), 'Generating random keystore...', True)

    keystore_name = generate_random_string(8)
    keystore_path = os.path.join(tempfile.gettempdir(), keystore_name)
    alias_name = 'CERT'
    passphase = generate_random_string(8)

    command = [
        tool_paths['keytool'],
        '-genkey',
        '-keystore', keystore_path,
        '-alias', alias_name,
        '-keyalg', 'RSA',
        '-keysize', '2048',
        '-validity', '10000'
    ]

    input = os.linesep.join(
        [passphase, passphase,
         '', '', '', '', '', '', 'yes'
         ]).encode()

    if not exec_tool(command, 'Error on generating keystore.', input=input, timeout=3):
        return

    dialog.gauge_update(
        int(WEIGHT*3), 'Signing APK with random keystore.', True)
    logger.info('Signing APK with random keystore.')

    command = [
        tool_paths['jarsigner'],
        '--sigalg', 'MD5withRSA',
        '--digestalg', 'SHA1',
        '-keystore', keystore_path,
        '-storepass', passphase,
        apk_out, alias_name
    ]

    if not exec_tool(command, 'Error on signing APK.', timeout=6):
        return

    dialog.gauge_update(100)
    dialog.gauge_stop()
    dialog.msgbox(f'Successfully generate APK at {apk_out}')
    logger.info(f'Successfully generate APK at {apk_out}')


if __name__ == '__main__':
    entry_point()
