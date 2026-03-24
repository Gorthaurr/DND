"""Export merged HuggingFace model to GGUF and register with Ollama."""

import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

MODELFILE_TEMPLATE = """FROM {gguf_path}

PARAMETER temperature 0.7
PARAMETER num_ctx 4096

TEMPLATE \"\"\"<|im_start|>system
{{{{ .System }}}}<|im_end|>
<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
\"\"\"

SYSTEM "You are a D&D Living World game engine. Respond ONLY in valid JSON."
"""


def export_to_gguf(
    merged_dir: Path,
    output_path: Path,
    quantization: str = "q4_k_m",
):
    """Convert merged HuggingFace model to GGUF using llama.cpp.

    Args:
        merged_dir: Path to the merged HF model directory.
        output_path: Destination path for the .gguf file.
        quantization: Quantization type (e.g. q4_k_m, q5_k_m, q8_0).
    """
    merged_dir = Path(merged_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fp16_path = output_path.with_suffix(".fp16.gguf")

    # Step 1: convert HF -> GGUF fp16
    logger.info("Converting HF model to GGUF fp16: %s", fp16_path)
    subprocess.run(
        [
            "python", "-m", "llama_cpp.convert",
            str(merged_dir),
            "--outfile", str(fp16_path),
            "--outtype", "f16",
        ],
        check=True,
    )

    # Step 2: quantize fp16 -> target quantization
    logger.info("Quantizing to %s: %s", quantization, output_path)
    subprocess.run(
        [
            "llama-quantize",
            str(fp16_path),
            str(output_path),
            quantization,
        ],
        check=True,
    )

    # Clean up intermediate fp16 file
    if fp16_path.exists():
        fp16_path.unlink()
        logger.info("Removed intermediate fp16 file")

    logger.info("GGUF export complete: %s", output_path)
    return output_path


def create_ollama_model(
    gguf_path: Path,
    model_name: str = "qwen2.5:14b-dnd",
):
    """Create Ollama Modelfile and register the model.

    Args:
        gguf_path: Path to the quantized .gguf file.
        model_name: Name for the Ollama model registry.
    """
    gguf_path = Path(gguf_path).resolve()

    modelfile_content = MODELFILE_TEMPLATE.format(gguf_path=gguf_path)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".Modelfile", delete=False, encoding="utf-8"
    ) as f:
        f.write(modelfile_content)
        modelfile_path = f.name

    logger.info("Created Modelfile at %s", modelfile_path)
    logger.info("Registering Ollama model: %s", model_name)

    subprocess.run(
        ["ollama", "create", model_name, "-f", modelfile_path],
        check=True,
    )

    # Clean up temp Modelfile
    Path(modelfile_path).unlink(missing_ok=True)

    logger.info("Ollama model '%s' created successfully.", model_name)
    return model_name
