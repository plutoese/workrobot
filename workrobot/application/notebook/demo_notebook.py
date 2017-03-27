# coding = UTF-8

import nbformat
from nbconvert import HTMLExporter, LatexExporter, MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
import matplotlib.pyplot as plt

notebook_filename = r'E:\github\workrobot\workrobot\application\notebook\try_two.ipynb'

ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

with open(notebook_filename) as f:
    nb = nbformat.read(f, as_version=4)
    print(nb)
    ep.preprocess(nb, {'metadata': {'path': r'E:\github\workrobot\workrobot\application\notebook'}})
    print(nb)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'basic'

    # 3. Process the notebook we loaded earlier
    (body, resources) = MarkdownExporter().from_notebook_node(nb)
    print(body)
    print(resources['outputs']['output_0_0.png'])
    with open('executed_notebook.ipynb', 'wt') as f:
        nbformat.write(nb, f)