import os
import random
import threading
import time
import yaml

from mcdreforged.api.all import *
from .utils import *


default_config = {
    "interval": 30,
    "prefix": "[Tips]"
}

interval = 30
prefix = "[Tips]"

tips = []

Task = False

tLock = threading.Lock()


def help() -> RTextList:
    return RTextList(
        psi.rtr(f"{plgSelf.id}.command_help.title") + "\n",
        psi.rtr(f"{plgSelf.id}.command_help.start") + "\n",
        psi.rtr(f"{plgSelf.id}.command_help.stop") + "\n",
        psi.rtr(f"{plgSelf.id}.command_help.reload") + "\n"
    )


def on_load(server: PluginServerInterface, prev_module):
    global tips, interval, prefix, Task
    server.logger.info(tr("on_load"))
    config = server.load_config_simple('config.json', default_config)
    server.register_command(
        Literal('!!tips')
        .then(
            Literal('start')
            .runs(
                lambda src: src.reply(manually_start())
            )
        )
        .then(
            Literal('stop')
            .runs(
                lambda src: src.reply(on_close())
            )
        )
        .then(
            Literal('reload')
            .runs(
                lambda src: src.reply(reload())
            )
        )
    )
    server.register_help_message('!!tips', help())
    interval = config["interval"]
    prefix = config['prefix']
    if not os.path.exists(f'{configDir}/tips.yml'):
        extract_file('resources/tips.yml', f'{configDir}/tips.yml')
    tips = load_config()
    if server.is_server_startup():
        Task = True
        psi.logger.info(tr("on_server_startup"))
        send_tips()


def load_config():
    with open(f'{configDir}/tips.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        tips = data.get('tips', None)
        if tips is not None:
            return tips
        else:
            return None


def on_server_startup(server: PluginServerInterface):
    global Task
    Task = True
    send_tips()


@new_thread("Tips-Broadcast")
def send_tips():
    try:
        prefixRText = RText.from_json_object(prefix)
    except ValueError:
        prefixRText = str(prefix)

    if tips is not None:
        with tLock:
            while Task:
                tip = random.choice(tips)
                try:
                    tip = RText.from_json_object(tip)
                except ValueError:
                    tip = str(tip)
                psi.broadcast(RText.join(" ", [prefixRText, tip]))
                time.sleep(interval)


def on_server_stop(server: PluginServerInterface, server_return_code: int):
    on_close()


def on_unload(server: PluginServerInterface):
    on_close()


def on_close():
    global Task
    Task = False
    return tr("on_close")


def manually_start():
    global Task
    if psi.is_server_startup():
        Task = True
        if not tLock.locked():
            send_tips()
            return tr("on_command.success")
        else:
            return tr("on_command.already_running")
    else:
        Task = False
        return tr("on_command.failed")


def reload():
    psi.reload_plugin(plgSelf.id)
    return tr("on_reload")
