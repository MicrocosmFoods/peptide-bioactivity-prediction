
from latch.types.metadata import (
    NextflowMetadata,
    LatchAuthor,
    NextflowRuntimeResources
)
from latch.types.directory import LatchDir

from .parameters import generated_parameters

NextflowMetadata(
    display_name='peptide_bioactivity_predictor',
    author=LatchAuthor(
        name="Elizabeth McDaniel",
    ),
    parameters=generated_parameters,
    runtime_resources=NextflowRuntimeResources(
        cpus=16,
        memory=20,
        storage_gib=100,
    ),
    log_dir=LatchDir("latch:///your_log_dir"),
)
