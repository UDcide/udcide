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
@click.argument("apk_path", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument("keywords", type=str, nargs=-1)
@click.option("-o", "apk_out", type=click.Path(file_okay=False), default="out")
def entry_point(apk_path, apk_out, keywords):
    def find_executable(executable, path=None):
        if not path:
            path = os.environ["PATH"]

        paths = path.split(os.pathsep)

        for p in paths:
            full_path = os.path.join(p, executable)
            if os.path.exists(full_path):
                return full_path

    def exec_tool(command, msg, input=None, timeout=None):
        try:
            process = run(
                command,
                stderr=STDOUT,
                stdout=PIPE,
                input=input,
                check=True,
                timeout=timeout,
            )
            logger.debug(process.stdout.decode())
            process.check_returncode()
        except CalledProcessError:
            if is_interactive():
                dialog.gauge_stop()
                dialog.msgbox(msg)
            logger.error(msg)
            return False

        return True

    def generate_random_string(length):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def is_interactive():
        return not keywords

    # Setup logger
    logger = logging.getLogger("UDcide-dlog")
    logger.setLevel(logging.DEBUG)
    ch_formater = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch = logging.FileHandler("udcide.log", "a")
    ch.setFormatter(ch_formater)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    if is_interactive():
        # Setup dialog
        dialog = Dialog(autowidgetsize=True)
        dialog.set_background_title("UDcide")
    else:
        # Direct logger to stderr
        stream = logging.StreamHandler()
        stream_formater = logging.Formatter("%(levelname)s: %(message)s")
        stream.setFormatter(stream_formater)
        stream.setLevel(logging.INFO)
        logger.addHandler(stream)

    # Find tools in $PATH
    if is_interactive():
        dialog.infobox("Detecting dependencies...")
    tools = ["apktool", "jarsigner", "keytool"]
    tool_paths = dict()
    for tool in tools:
        path = find_executable(tool)
        if path:
            tool_paths[tool] = path

    missed_tools = [tool for tool in tools if tool not in tool_paths]
    if missed_tools:
        msg = f'Cannot found {",".join(missed_tools)} in PATH.'
        if is_interactive():
            dialog.msgbox(msg)
        logger.error(msg)
        return

    # Download Quark Rules
    if not os.path.exists(config.DIR_PATH):
        msg = "Downloading Quark rules..."
        if is_interactive():
            dialog.infobox(msg)
        logger.info(msg)
        download()

    # Run Quark analysis
    msg = "Analysing APK with Quark-Engine."
    if is_interactive():
        dialog.gauge_start(msg)
    logger.info(msg)

    rule_dir = config.DIR_PATH
    quark = Quark(apk_path)
    rule_list = [x for x in os.listdir(rule_dir) if x.endswith("json")]

    factor = 100 / len(rule_list)
    behavior_list = []
    for index, rule in enumerate(rule_list):
        rule_path = os.path.join(rule_dir, rule)
        checker = QuarkRule(rule_path)

        if is_interactive():
            dialog.gauge_update(int(factor * index), checker.crime, True)

        quark.run(checker)
        parents = quark.quark_analysis.level_5_result
        if parents:
            behavior_list.append(
                Crime(checker.crime, list((str(p.full_name) for p in parents)))
            )

    if is_interactive():
        dialog.gauge_stop()

    # Select behavior
    if is_interactive():
        logger.info("Waiting for user to select behavires.")

        code, tags = dialog.checklist(
            "Select behaviores to disable.",
            choices=[(c.description, "", False) for c in behavior_list],
        )
        if code == dialog.CANCEL:
            logger.info("Canceled by user.")
            return

        selected_list = []
        for behavior in behavior_list:
            if behavior.description in tags:
                selected_list.extend(behavior.sequences)

    else:
        selected_list = []
        tags = []
        for behavior in behavior_list:
            for keyword in keywords:
                if keyword in behavior.description:
                    tags.append(behavior.description)
                    selected_list.extend(behavior.sequences)

    if not selected_list:
        msg = "Nothing seleceted by user."
        if is_interactive():
            dialog.msgbox(msg)
        logger.warning(msg)
        return

    logger.info(f"Selected: {tags}")

    smali_dir = TemporaryDirectory("udcide").name
    apk_out = os.path.join(apk_out, os.path.basename(apk_path))

    TOTAL_STAGE = 4
    WEIGHT = 100 / TOTAL_STAGE
    # Unpack APK
    msg = "Unpacking APK..."
    if is_interactive():
        dialog.gauge_start(msg)
    logger.info(msg)

    command = [tool_paths["apktool"], "d", "-r", "-f", "-o", smali_dir, apk_path]

    if not exec_tool(command, "Error on unpacking APK", input=b"b"):
        return

    # Modify APK
    msg = "Modifying APK..."
    if is_interactive():
        dialog.gauge_update(int(WEIGHT * 1), msg, True)
    logger.info(msg)

    udcide = UDcide(apk_path, os.path.join(smali_dir, "smali"))
    udcide.batch_disable(selected_list)

    # Pack APK
    msg = "Repacking APK..."
    if is_interactive():
        dialog.gauge_update(int(WEIGHT * 2), msg, True)
    logger.info(msg)

    command = [tool_paths["apktool"], "b", "-o", apk_out, smali_dir]

    if not exec_tool(command, "Error on repacking APK", input=b"b"):
        return

    # Sign APK
    # Generate random keystore
    msg = "Generating random keystore..."
    logger.info(msg)
    if is_interactive():
        dialog.gauge_update(int(WEIGHT * 3), msg, True)

    keystore_name = generate_random_string(8)
    keystore_path = os.path.join(tempfile.gettempdir(), keystore_name)
    alias_name = "CERT"
    passphase = generate_random_string(8)

    command = [
        tool_paths["keytool"],
        "-genkey",
        "-keystore",
        keystore_path,
        "-alias",
        alias_name,
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "10000",
    ]

    input = os.linesep.join(
        [passphase, passphase, "", "", "", "", "", "", "yes"]
    ).encode()

    if not exec_tool(command, "Error on generating keystore.", input=input):
        return

    msg = "Signing..."
    if is_interactive():
        dialog.gauge_update(int(WEIGHT * 3), msg, True)
    logger.info(msg)

    command = [
        tool_paths["jarsigner"],
        "--sigalg",
        "MD5withRSA",
        "--digestalg",
        "SHA1",
        "-keystore",
        keystore_path,
        "-storepass",
        passphase,
        apk_out,
        alias_name,
    ]

    if not exec_tool(command, "Error on signing APK.", timeout=60):
        return

    msg = f"Successfully generate APK at {apk_out}"
    if is_interactive():
        dialog.gauge_update(100)
        dialog.gauge_stop()
        dialog.msgbox(msg)
    logger.info(msg)


if __name__ == "__main__":
    entry_point()
