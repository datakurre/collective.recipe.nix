Creating Nix-expressions with Docker
====================================

Create Nix-builder for Docker:

.. code:: bash

   $ git clone https://github.com/datakurre/nix-build-pack-docker
   $ cd nix-buildpack-docker/builder
   $ docker build -t nix-build-pack --rm=true --force-rm=true --no-cache=true .

Create collective.recipe.nix image for Docker:

.. code:: bash

   $ cd ../..
   $ docker run --rm -v `pwd`:/opt nix-build-pack /opt/buildout.nix
   $ docker build -t buildout --rm=true --force-rm=true --no-cache=true .

Create Nix-expression with Docker container:

.. code:: bash

   $ cd ../examples
   $ docker run --rm -v `pwd`:/opt -v /tmp:/tmp -w /opt buildout -c releaser.cfg
