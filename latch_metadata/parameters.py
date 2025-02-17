
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input_fastas': NextflowParameter(
        type=LatchDir,
        default=None,
        section_title='Input/output options',
        description='Directory of input FASTA peptides for bioactivity prediction.',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'peptides_db': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title='Databases',
        description='FASTA of known peptides for comparison to input peptides.',
    ),
    'models_list': NextflowParameter(
        type=LatchFile,
        default=None,
        section_title=None,
        description='TXT file of list of models that are located in the models_dir that you want to be run for bioactivity prediction.',
    ),
    'models_dir': NextflowParameter(
        type=LatchDir,
        default=None,
        section_title=None,
        description='Directory of ML classification models to predict bioactivity.',
    ),
}

