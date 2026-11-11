# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Regression tests for Astroovoo/p06-Astroovoo issue 4 (thumbor#1711):
# extreme resize and fit-in requests on the tracked course images.

from pathlib import Path

from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context, RequestParameters, ServerParameters
from thumbor.importer import Importer
from thumbor.transformer import Transformer

IMAGES = Path(__file__).resolve().parent.parent / "course" / "images"


class ExtremeResizeTestCase(TestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    async def run_transform(self, name, **params):
        context = self.get_context()
        engine = context.modules.engine
        engine.load((IMAGES / name).read_bytes(), ".png")
        context.request = RequestParameters(crop={"left": 0, "top": 0, "right": 0, "bottom": 0})
        context.request.engine = engine
        context.request.focal_points = []
        context.request.stretch = False
        context.request.adaptive = False
        context.request.full = False
        context.request.debug = False
        context.request.fit_in = False
        for key, value in params.items():
            setattr(context.request, key, value)
        await Transformer(context).transform()
        return context.modules.engine

    @gen_test
    async def test_wide_strip_from_rainbow_is_not_blank(self):
        engine = await self.run_transform(
            "rainbow.png", width=800, height=20
        )

        assert engine.size == (800, 20)
        alpha = engine.image.getchannel("A")
        assert alpha.getextrema()[1] > 0

    @gen_test
    async def test_fit_in_1x1_returns_1x1_image(self):
        engine = await self.run_transform(
            "940x2.png", fit_in=True, width=1, height=1
        )

        assert engine.size == (1, 1)

    @gen_test
    async def test_fit_in_width_only_returns_100x1_image(self):
        engine = await self.run_transform(
            "940x2.png", fit_in=True, width=100, height=0
        )

        assert engine.size == (100, 1)
