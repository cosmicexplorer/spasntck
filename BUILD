python_library(
    name='library',
    sources=['**/*.py'],
)

python_distribution(
    name='plugin',
    dependencies=[':library'],
    setup_py_commands=['bdist_wheel'],
    provides=setup_py(
        name='spasntck',
        description='Marrying Spack HPC environments with Pants caching.',
        version='0.0.1',
    ),
)
