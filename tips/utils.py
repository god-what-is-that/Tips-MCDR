from mcdreforged.api.all import *

psi = ServerInterface.psi()
plgSelf = psi.get_self_metadata()
configDir = psi.get_data_folder()

def tr(tr_key: str):
    if tr_key.startswith(f"{plgSelf.id}"):
        translation = psi.rtr(f"{tr_key}")
    else:
        if tr_key.startswith("#"):
            translation = psi.rtr(tr_key.replace("#", ""))
        else:
            translation = psi.rtr(f"{plgSelf.id}.{tr_key}")
    translation: str = str(translation)
    return translation

def extract_file(file_path, target_path):
    with psi.open_bundled_file(file_path) as file_handler:
        with open(target_path, 'wb') as target_file:
            target_file.write(file_handler.read())