#
# This file is autogenerated during plugin quickstart and overwritten during
# plugin makedist. DO NOT CHANGE IT if you plan to use plugin makedist to update 
# the distribution.
#

from setuptools import setup, find_packages

kwargs = {'author': 'Tristan A. Hearn',
 'author_email': 'tristan.a.hearn@nasa.gov',
 'classifiers': ['Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering'],
 'description': 'OpenMDAO implementation of the Aerovelo Atlas human-powered helicopter design problem',
 'download_url': '',
 'entry_points': u'[openmdao.component]\nAtlas.properties.SparProperties=Atlas.properties:SparProperties\nAtlas.properties.DiscretizeProperties=Atlas.properties:DiscretizeProperties\nAtlas.lift_drag.liftDrag=Atlas.lift_drag:liftDrag\nAtlas.vortex.inducedVelocity=Atlas.vortex:inducedVelocity\nAtlas.structures.Strains=Atlas.structures:Strains\nAtlas.structures.QuadSparProperties=Atlas.structures:QuadSparProperties\nAtlas.structures.JointSparProperties=Atlas.structures:JointSparProperties\nAtlas.structures.MassProperties=Atlas.structures:MassProperties\nAtlas.properties.ChordProperties=Atlas.properties:ChordProperties\nAtlas.coefficients.dragCoefficient=Atlas.coefficients:dragCoefficient\nAtlas.structures.Failures=Atlas.structures:Failures\nAtlas.vortex.vortexRing=Atlas.vortex:vortexRing\nAtlas.structures.FEM=Atlas.structures:FEM\nAtlas.structures.Structures=Atlas.structures:Structures\n\n[openmdao.container]\nAtlas.properties.DiscretizeProperties=Atlas.properties:DiscretizeProperties\nAtlas.lift_drag.liftDrag=Atlas.lift_drag:liftDrag\nAtlas.structures.Failure=Atlas.structures:Failure\nAtlas.lift_drag.Fblade=Atlas.lift_drag:Fblade\nAtlas.structures.Strain=Atlas.structures:Strain\nAtlas.structures.JointProperties=Atlas.structures:JointProperties\nAtlas.properties.SparProperties=Atlas.properties:SparProperties\nAtlas.structures.Strains=Atlas.structures:Strains\nAtlas.vortex.vortexRing=Atlas.vortex:vortexRing\nAtlas.vortex.inducedVelocity=Atlas.vortex:inducedVelocity\nAtlas.structures.JointSparProperties=Atlas.structures:JointSparProperties\nAtlas.structures.FEM=Atlas.structures:FEM\nAtlas.structures.Structures=Atlas.structures:Structures\nAtlas.structures.BucklingFailure=Atlas.structures:BucklingFailure\nAtlas.structures.Flags=Atlas.structures:Flags\nAtlas.structures.MaterialFailure=Atlas.structures:MaterialFailure\nAtlas.structures.PrescribedLoad=Atlas.structures:PrescribedLoad\nAtlas.structures.QuadSparProperties=Atlas.structures:QuadSparProperties\nAtlas.structures.MassProperties=Atlas.structures:MassProperties\nAtlas.properties.ChordProperties=Atlas.properties:ChordProperties\nAtlas.coefficients.dragCoefficient=Atlas.coefficients:dragCoefficient\nAtlas.structures.Failures=Atlas.structures:Failures',
 'include_package_data': True,
 'install_requires': ['openmdao.main'],
 'keywords': ['openmdao'],
 'license': 'Apache 2.0',
 'maintainer': 'Tristan A. Hearn',
 'maintainer_email': 'tristan.a.hearn@nasa.gov',
 'name': 'Atlas',
 'package_data': {'Atlas': ['sphinx_build/html/index.html',
                            'sphinx_build/html/py-modindex.html',
                            'sphinx_build/html/objects.inv',
                            'sphinx_build/html/pkgdocs.html',
                            'sphinx_build/html/.buildinfo',
                            'sphinx_build/html/usage.html',
                            'sphinx_build/html/searchindex.js',
                            'sphinx_build/html/search.html',
                            'sphinx_build/html/srcdocs.html',
                            'sphinx_build/html/genindex.html',
                            'sphinx_build/html/_modules/index.html',
                            'sphinx_build/html/_modules/Atlas/failure.html',
                            'sphinx_build/html/_modules/Atlas/vortex.html',
                            'sphinx_build/html/_modules/Atlas/properties.html',
                            'sphinx_build/html/_modules/Atlas/structures.html',
                            'sphinx_build/html/_modules/Atlas/coefficients.html',
                            'sphinx_build/html/_modules/Atlas/lift_drag.html',
                            'sphinx_build/html/_modules/Atlas/test/test_coefficients.html',
                            'sphinx_build/html/_modules/Atlas/test/test_failure.html',
                            'sphinx_build/html/_modules/Atlas/test/test_vortex.html',
                            'sphinx_build/html/_modules/Atlas/test/test_properties.html',
                            'sphinx_build/html/_modules/Atlas/test/test_structures.html',
                            'sphinx_build/html/_modules/Atlas/test/test_lift_drag.html',
                            'sphinx_build/html/_modules/Atlas/test/testvals.html',
                            'sphinx_build/html/_static/default.css',
                            'sphinx_build/html/_static/plus.png',
                            'sphinx_build/html/_static/websupport.js',
                            'sphinx_build/html/_static/minus.png',
                            'sphinx_build/html/_static/searchtools.js',
                            'sphinx_build/html/_static/doctools.js',
                            'sphinx_build/html/_static/file.png',
                            'sphinx_build/html/_static/comment-bright.png',
                            'sphinx_build/html/_static/basic.css',
                            'sphinx_build/html/_static/ajax-loader.gif',
                            'sphinx_build/html/_static/pygments.css',
                            'sphinx_build/html/_static/sidebar.js',
                            'sphinx_build/html/_static/comment.png',
                            'sphinx_build/html/_static/jquery.js',
                            'sphinx_build/html/_static/up-pressed.png',
                            'sphinx_build/html/_static/up.png',
                            'sphinx_build/html/_static/underscore.js',
                            'sphinx_build/html/_static/down-pressed.png',
                            'sphinx_build/html/_static/comment-close.png',
                            'sphinx_build/html/_static/down.png',
                            'sphinx_build/html/_sources/pkgdocs.txt',
                            'sphinx_build/html/_sources/usage.txt',
                            'sphinx_build/html/_sources/index.txt',
                            'sphinx_build/html/_sources/srcdocs.txt',
                            'test/mass.mat',
                            'test/test_vortex.py',
                            'test/testvals.py',
                            'test/test_lift_drag.py',
                            'test/strains.mat',
                            'test/__init__.py',
                            'test/StrCalc.mat',
                            'test/FEM.mat',
                            'test/failure.mat',
                            'test/test_structures.py',
                            'test/test_coefficients.py',
                            'test/test_properties.py',
                            'test/openmdao_log.txt']},
 'package_dir': {'': 'src'},
 'packages': ['Atlas', 'Atlas.test'],
 'url': '',
 'version': '0.1',
 'zip_safe': False}


setup(**kwargs)

