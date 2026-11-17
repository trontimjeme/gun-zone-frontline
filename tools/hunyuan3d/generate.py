"""Generate a Gun ZONE character GLB from a reference image."""
import argparse
import gc
import math
import os
import tempfile
from pathlib import Path


def normalize_character(mesh, height):
    import numpy as np

    bounds = mesh.bounds
    if bounds is None or not np.isfinite(bounds).all():
        raise ValueError("Generated mesh has invalid bounds.")
    extent = float(bounds[1, 1] - bounds[0, 1])
    if extent <= 0 or len(mesh.faces) == 0:
        raise ValueError("Generated mesh is empty or has zero height.")
    center = (bounds[0] + bounds[1]) * 0.5
    mesh.apply_translation([-center[0], -bounds[0, 1], -center[2]])
    mesh.apply_scale(height / extent)
    return mesh


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--texture", action="store_true")
    parser.add_argument("--keep-background", action="store_true")
    parser.add_argument("--height", type=float, default=1.7732026344)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--faces", type=int, default=30000)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error("Input image does not exist.")
    if args.output.suffix.lower() != ".glb":
        parser.error("Output must have a .glb extension.")
    if not math.isfinite(args.height) or args.height <= 0 or args.steps < 1 or args.faces < 4:
        parser.error("Height and steps must be positive. Face target must be at least 4.")
    if args.output.exists():
        parser.error("Output already exists. Choose a new output filename.")

    import torch
    from PIL import Image, ImageOps
    from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline, FaceReducer

    if not torch.cuda.is_available():
        parser.error("This workflow requires CUDA-enabled PyTorch and an NVIDIA GPU.")
    with Image.open(args.image) as source:
        image = ImageOps.exif_transpose(source).convert("RGBA")
    if not args.keep_background and image.getchannel("A").getextrema() == (255, 255):
        from hy3dgen.rembg import BackgroundRemover
        image = BackgroundRemover()(image)
    generator = torch.Generator(device="cuda").manual_seed(args.seed)
    pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained("tencent/Hunyuan3D-2")
    mesh = pipeline(image=image, num_inference_steps=args.steps, generator=generator)[0]
    del pipeline
    gc.collect()
    torch.cuda.empty_cache()
    if len(mesh.faces) > args.faces:
        mesh = FaceReducer()(mesh, max_facenum=args.faces)
    if args.texture:
        from hy3dgen.texgen import Hunyuan3DPaintPipeline
        paint = Hunyuan3DPaintPipeline.from_pretrained("tencent/Hunyuan3D-2")
        mesh = paint(mesh, image=image)
    normalize_character(mesh, args.height)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(suffix=".glb", dir=output.parent)
    os.close(fd)
    try:
        mesh.export(temporary, file_type="glb")
        # Exclusive creation preserves an existing file if another job finished first.
        with output.open("xb") as destination, open(temporary, "rb") as source:
            import shutil
            shutil.copyfileobj(source, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f"Exported {output} ({len(mesh.faces)} triangles, height {args.height:.3f} m).")
    print("Next step: rigging, animation retargeting and in-game movement validation.")


if __name__ == "__main__":
    main()
