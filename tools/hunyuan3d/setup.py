"""Prepare the pinned Hunyuan3D source in a dedicated Python environment."""
import argparse
import subprocess
import sys
import venv
from pathlib import Path

REPOSITORY = "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git"
REVISION = "f8db63096c8282cb27354314d896feba5ba6ff8a"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--texture", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    root.mkdir(parents=True, exist_ok=True)
    source = root / "Hunyuan3D-2"
    environment = root / "venv"
    if not source.exists():
        subprocess.run(["git", "clone", REPOSITORY, str(source)], check=True)
    remote = subprocess.check_output(
        ["git", "-C", str(source), "remote", "get-url", "origin"], text=True
    ).strip()
    if remote.removesuffix(".git") != REPOSITORY.removesuffix(".git"):
        parser.error("Workspace contains a different source repository.")
    dirty = subprocess.check_output(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    ).strip()
    if dirty:
        parser.error("Source has edited tracked files. Use another workspace.")
    subprocess.run(["git", "-C", str(source), "fetch", "origin", REVISION], check=True)
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", REVISION], check=True)
    if not (environment / "pyvenv.cfg").exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    gpu = subprocess.run(
        [str(python), "-c", "import torch; assert torch.cuda.is_available()"],
        capture_output=True, text=True,
    )
    if gpu.returncode:
        print(f"Environment ready at {environment}")
        print("Install CUDA-enabled torch and torchvision in this environment, then rerun setup.")
        print(f'Python executable: "{python}"')
        return 2
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(source / "requirements.txt")], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "-e", str(source)], check=True)
    if args.texture:
        for component in ("custom_rasterizer", "differentiable_renderer"):
            subprocess.run(
                [str(python), "setup.py", "install"],
                cwd=source / "hy3dgen" / "texgen" / component, check=True,
            )
    print(f'Ready. Run generate.py using "{python}".')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
